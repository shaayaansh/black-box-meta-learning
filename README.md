# black-box-meta-learning
meta learning for few shot image classification

This is a solution for Stanford CS330 Meta Learning and Multi-task learning course, HW1.

Here we implement a sequential network (LSTM) to learn labels from a set of K-shot labeled data. 

## Data sampling
To sample data for K-shot N-ways classification, we select N characters from each alphabet, and randomly sample K+1 images for each character. We use one-hot encoding for labeling the characters in each batch. Every instance in the batch has N images, one for each character, in the same order. The final instance in the batch, which is the query set, has one image per character, but in a different order than the training data.


