import os
import numpy as np
from pylearn2.datasets import dense_design_matrix
from pylearn2.utils import serial
from pylearn2.utils.string_utils import preprocess
import tables
import os

class SeqDataset(dense_design_matrix.DenseDesignMatrix):
    def __init__(self, which_set, shuffle=True):

        assert which_set in ['train', 'test', 'val']
        if which_set == 'train':
            path = '/u/aggarwal/alignData/train_with_splits/train/'
            #path = '/u/aggarwal/alignData/oldData/afew2_with_splits/train/'
        elif which_set == 'val':
            path = '/u/aggarwal/alignData/train_with_splits/val/'
            #path = '/u/aggarwal/alignData/oldData/afew2_with_splits/val/'
        elif which_set == 'test':
            path = '/u/aggarwal/alignData/test_final_to_be_used/'
            #path = '/u/aggarwal/alignData/oldData/afew2_test_final/'
        
        mode = 'r'

        #parse through the path

        self.which_set = which_set
        self.paths = []
        self.emotions = []
        self.perturbations = []        
        self.flipped = []
        self.numSamples = 0
        self.clipIDs = []
        for root, subdir, files in os.walk(path):
            for file in files:
                if os.path.splitext(file)[-1] in ('.npy',):
                    #print file.split('_')
                    self.numSamples += 1
                    if which_set in ('train', 'val'):
                        clipID = int(file.split('_')[4])
                        for emotion in ['Happy', 'Disgust', 'Neutral', 'Fear', 'Surprise', 'Sad', 'Angry']:
                            if emotion in file:
                                emotionThis = emotion
                                break
                        self.emotions.append(emotionThis)
                    else:
                        clipID = int(file.split('_')[4])
                        emotionThis = 'unknown'
                    for pert in ['_1_', 'org', '_2_', '_3_', '_4_']:
                        if pert  in file:
                            if pert[1] in ('1', '2', '3', '4'):
                                perturbation = pert[1]
                            else:
                                perturbation = '0'
                            break
                            
                    flip = 'flip' in file
                    #print flip, perturbation, emotionThis, clipID, file
                    self.flipped.append(flip)
                    self.perturbations.append(perturbation)
                    self.paths.append(os.path.join(root, file))
                    self.clipIDs.append(clipID)

        self.indices = np.asarray(range(self.numSamples))
        if shuffle:
            rng = np.random.RandomState(42)
            rng.shuffle(self.indices)
              

    def __len__(self):
        return self.numSamples
    
    def get_clip(self, index):
        index = self.indices[index]
        clip = np.memmap(self.paths[index], dtype='float32', mode='r')
        numSamples = len(clip)/(48*48)
        clip = clip.reshape(numSamples, 48*48)
        if self.which_set == 'test':
            return (clip, None, self.paths[index])
        else:
            return (clip, self.emotions[index], self.paths[index])

    def get_filtered_indices(self, perturbations = ['0', '1', '2', '3', '4'], flips = [True, False]):
        indices = []
        
        for i in range(self.numSamples):
            index = self.indices[i]
            perturbation = self.perturbations[index]
            flip = self.flipped[index]
            if flip in flips and perturbation in perturbations:
                indices.append(index)
    
        return indices

        

if __name__ == "__main__":
    obj =  SeqDataset(which_set = 'test', shuffle = True)
    print 'Number of clips:', len(obj)
    print obj.get_clip(67)
    print len(obj.get_filtered_indices(perturbations = ['4'], flips = [True]))

    

