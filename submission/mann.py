import torch
from torch import nn, Tensor
import torch.nn.functional as F


def initialize_weights(model):
    if type(model) in [nn.Linear]:
        nn.init.xavier_uniform_(model.weight)
        nn.init.zeros_(model.bias)
    elif type(model) in [nn.LSTM, nn.RNN, nn.GRU]:
        nn.init.orthogonal_(model.weight_hh_l0)
        nn.init.xavier_uniform_(model.weight_ih_l0)
        nn.init.zeros_(model.bias_hh_l0)
        nn.init.zeros_(model.bias_ih_l0)


class MANN(nn.Module):
    def __init__(self, num_classes, samples_per_class, hidden_dim):
        super(MANN, self).__init__()
        self.num_classes = num_classes
        self.samples_per_class = samples_per_class

        self.layer1 = torch.nn.LSTM(num_classes + 784, hidden_dim, batch_first=True)
        self.layer2 = torch.nn.LSTM(hidden_dim, num_classes, batch_first=True)
        initialize_weights(self.layer1)
        initialize_weights(self.layer2)

    def forward(self, input_images, input_labels):
        """
        MANN
        Args:
            input_images: [B, K+1, N, 784] flattened images
            labels: [B, K+1, N, N] ground truth labels
        Returns:
            [B, K+1, N, N] predictions
        """
        #############################
        ### START CODE HERE ###
        
        # Step 1: Concatenate the full (support & query) set of labels and images
        labels_clone = input_labels.detach().clone()

        # Step 2: Zero out the labels from the concatenated corresponding to the query set
        labels_clone[:, -1, :, :] = torch.zeros_like(labels_clone[:, -1, :, :])
        inputs = torch.cat((input_images, labels_clone), dim=-1)
        inputs = inputs.view(inputs.shape[0], -1, inputs.shape[3])
        # Step 3: Pass the concatenated set sequentially to the memory-augmented network
        output_1, _ = self.layer1(inputs.float())
        output_2, _ = self.layer2(output_1)
        # Step 3: Return the predictions with [B, K+1, N, N] shape
        output = output_2.view(inputs.shape[0], self.samples_per_class, self.num_classes, self.num_classes)
        return output

        ### END CODE HERE ###

    def loss_function(self, preds, labels):
        """
        Computes MANN loss
        Args:
            preds: [B, K+1, N, N] network output
            labels: [B, K+1, N, N] labels
        Returns:
            scalar loss
        Note:
            Loss should only be calculated on the N test images
            Loss should be a scalar since mean reduction is used for cross entropy loss
            You would want to use F.cross_entropy here, specifically:
            with predicted unnormalized logits as input and ground truth class indices as target.
            Your logits would be of shape [B*N, N], and label indices would be of shape [B*N].
        """
        loss = None

        # Step 1: extract the predictions for the query set
        preds_target = preds[:, -1, :, :].reshape(-1, preds.shape[-1])
        # Step 2: extract the true labels for the query set and reverse the one hot-encoding  
        labels_target = labels[:, -1, :, :].reshape(-1, labels.shape[-1])
        
        # Step 3: compute the Cross Entropy Loss for the query set only!
        loss = F.cross_entropy(preds_target, labels_target)
        return loss

        

