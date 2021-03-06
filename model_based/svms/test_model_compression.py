
import sys
import os
import time

from basic.common import ROOT_PATH,checkToSkip,makedirsforfile
from basic.util import readImageSet
from simpleknn.bigfile import BigFile, StreamFile
from basic.annotationtable import readConcepts,readAnnotationsFrom
from basic.metric import getScorer


if __name__ == "__main__":
    try:
        rootpath = sys.argv[1]
    except:
        rootpath = ROOT_PATH

    metric = 'AP'
    feature = "dsift"
    
    trainCollection = 'voc2008train'
    trainAnnotationName = 'conceptsvoc2008train.txt'
    testCollection = 'voc2008val'
    testAnnotationName = 'conceptsvoc2008val.txt'
    testset = testCollection

    modelName = 'fik50' 
    modelName = 'fastlinear'
    if 'fastlinear' == modelName:
        from fastlinear.fastlinear import fastlinear_load_model as load_model
    else:
        from fiksvm.fiksvm import fiksvm_load_model as load_model


    scorer = getScorer(metric)
    
    

    imset = readImageSet(testCollection,testset,rootpath=rootpath)
    concepts = readConcepts(testCollection,testAnnotationName,rootpath=rootpath)
    feat_dir = os.path.join(rootpath, testCollection, "FeatureData", feature)
    feat_file = BigFile(feat_dir)

    _renamed, _vectors = feat_file.read(imset)

    nr_of_images = len(_renamed)
    nr_of_concepts = len(concepts)
    
    mAP = 0.0
    models = [None] * len(concepts)


    for i,concept in enumerate(concepts):
        model_file_name = os.path.join(rootpath,trainCollection,'Models',trainAnnotationName,feature, modelName, '%s.model'%concept)
        model1 = load_model(model_file_name)
        (pA,pB) = model1.get_probAB()
        

        model2 = load_model(model_file_name)
        model2.add_fastsvm(model1, 0.8, 1)

        names,labels = readAnnotationsFrom(testCollection, testAnnotationName, concept, rootpath=rootpath)
        name2label = dict(zip(names,labels))

        ranklist1 = [(_id, model1.predict(_vec)) for _id,_vec in zip(_renamed, _vectors)]
        ranklist2 = [(_id, model2.predict(_vec)) for _id,_vec in zip(_renamed, _vectors)]
        

        model_file_name = os.path.join(rootpath,trainCollection,'Models', 'bag' + trainAnnotationName,feature, modelName, '%s.model'%concept)
        model3 = load_model(model_file_name)
        ranklist3 = [(_id, model3.predict(_vec)) for _id,_vec in zip(_renamed, _vectors)]
        
        print concept,

        for ranklist in [ranklist1, ranklist2, ranklist3]:
            ranklist.sort(key=lambda v:v[1], reverse=True)
            sorted_labels = [name2label[x[0]] for x in ranklist if x[0] in name2label]
            print '%.3f'%scorer.score(sorted_labels),
        print ''


    
        
