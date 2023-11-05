# -*- coding: utf-8 -*-
"""Email  SPAM CLASSIFICATION USING PYSPARK.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1g209HnsrEzGW4vmPA1-MHRiqxGuFX7v3

https://archive.ics.uci.edu/dataset/228/sms+spam+collection - Dataset
"""

!pip install pyspark

import pyspark

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("spamclassification").getOrCreate()
spark

data = spark.read.csv("/content/SMSSpamCollection.csv",inferSchema=True,sep='\t')
data = data.withColumnRenamed('_c0','class').withColumnRenamed('_c1','text')

data.show()

"""Clean and Prepare the Data:"""

from pyspark.sql.functions import length
data = data.withColumn('length',length(data['text']))
data.show()

data.groupby('class').mean().show()

"""Feature Transformations:"""

from pyspark.ml.feature import Tokenizer,StopWordsRemover, CountVectorizer,IDF,StringIndexer
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.linalg import Vector

tokenizer = Tokenizer(inputCol="text", outputCol="token_text")

stopremove = StopWordsRemover(inputCol='token_text',outputCol='stop_tokens')

count_vec = CountVectorizer(inputCol='stop_tokens',outputCol='c_vec')

idf = IDF(inputCol="c_vec", outputCol="tf_idf")

ham_spam_to_num = StringIndexer(inputCol='class',outputCol='label')

clean_up = VectorAssembler(inputCols=['tf_idf','length'],outputCol='features')

from pyspark.ml.linalg import Vector

"""Model 1 - Naive Bayes"""

from pyspark.ml.classification import NaiveBayes
# Use defaults
nb = NaiveBayes()

"""Pipeline"""

from pyspark.ml import Pipeline
data_prep_pipe = Pipeline(stages=[ham_spam_to_num,tokenizer,stopremove,count_vec,idf,clean_up])
cleaner = data_prep_pipe.fit(data)
clean_data = cleaner.transform(data)

"""Displaying the Output after Pre-processing"""

clean_data = clean_data.select(['label','features'])
clean_data.show()

(training,testing) = clean_data.randomSplit([0.7,0.3])

spam_predictor_1 = nb.fit(training)

data.printSchema()

test_results_1 = spam_predictor_1.transform(testing)

test_results_1.show()

from pyspark.ml.evaluation import MulticlassClassificationEvaluator
acc_eval = MulticlassClassificationEvaluator()
acc_1 = acc_eval.evaluate(test_results_1)
print("Accuracy of model at predicting spam was: {}".format(acc_1))