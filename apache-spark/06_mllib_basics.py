"""
Example 6: MLlib Basics - Machine Learning with Spark

This example demonstrates:
- Feature engineering (VectorAssembler, StringIndexer)
- Classification (Logistic Regression, Decision Tree)
- Regression (Linear Regression)
- Model evaluation
- Pipeline API

WHAT IT DOES:
Introduces Spark MLlib for distributed machine learning.

HOW TO RUN:
python 06_mllib_basics.py

EXPECTED OUTPUT:
Console output showing ML model training and evaluation.
"""

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StringIndexer, StandardScaler
from pyspark.ml.classification import LogisticRegression, DecisionTreeClassifier
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator, RegressionEvaluator
from pyspark.ml import Pipeline
from pyspark.sql.functions import col


def create_spark_session():
    """Create SparkSession."""
    spark = SparkSession.builder \
        .appName("MLlib Basics") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def feature_engineering():
    """
    Feature engineering with MLlib.
    """
    print("\n" + "="*60)
    print("1. FEATURE ENGINEERING")
    print("="*60)
    
    spark = create_spark_session()
    
    # Sample data
    data = [
        (1, "A", 25, 50000),
        (2, "B", 30, 60000),
        (3, "A", 35, 70000),
        (4, "C", 28, 55000),
        (5, "B", 32, 65000)
    ]
    df = spark.createDataFrame(data, ["id", "category", "age", "salary"])
    
    print("\nOriginal data:")
    df.show()
    
    # StringIndexer: Convert categorical to numeric
    indexer = StringIndexer(inputCol="category", outputCol="category_index")
    indexed_df = indexer.fit(df).transform(df)
    
    print("\nAfter StringIndexer:")
    indexed_df.show()
    
    # VectorAssembler: Combine features into vector
    assembler = VectorAssembler(
        inputCols=["category_index", "age"],
        outputCol="features"
    )
    feature_df = assembler.transform(indexed_df)
    
    print("\nAfter VectorAssembler:")
    feature_df.select("id", "features", "salary").show(truncate=False)
    
    # StandardScaler: Normalize features
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
    scaler_model = scaler.fit(feature_df)
    scaled_df = scaler_model.transform(feature_df)
    
    print("\nAfter StandardScaler:")
    scaled_df.select("id", "scaled_features").show(truncate=False)
    
    spark.stop()


def logistic_regression_example():
    """
    Binary classification with Logistic Regression.
    """
    print("\n" + "="*60)
    print("2. LOGISTIC REGRESSION (Classification)")
    print("="*60)
    
    spark = create_spark_session()
    
    # Sample data: predict if salary > 60000
    data = [
        (25, 50000, 0),
        (30, 65000, 1),
        (35, 75000, 1),
        (28, 55000, 0),
        (32, 70000, 1),
        (26, 52000, 0),
        (38, 80000, 1),
        (29, 58000, 0),
        (33, 68000, 1),
        (27, 54000, 0)
    ]
    df = spark.createDataFrame(data, ["age", "experience", "high_salary"])
    
    print("\nTraining data:")
    df.show()
    
    # Prepare features
    assembler = VectorAssembler(
        inputCols=["age", "experience"],
        outputCol="features"
    )
    feature_df = assembler.transform(df)
    
    # Split data
    train_df, test_df = feature_df.randomSplit([0.7, 0.3], seed=42)
    
    print(f"\nTraining set: {train_df.count()} rows")
    print(f"Test set: {test_df.count()} rows")
    
    # Train model
    lr = LogisticRegression(
        featuresCol="features",
        labelCol="high_salary",
        maxIter=10
    )
    model = lr.fit(train_df)
    
    print(f"\nCoefficients: {model.coefficients}")
    print(f"Intercept: {model.intercept}")
    
    # Make predictions
    predictions = model.transform(test_df)
    
    print("\nPredictions:")
    predictions.select("age", "experience", "high_salary", "prediction", "probability").show(truncate=False)
    
    # Evaluate
    evaluator = BinaryClassificationEvaluator(labelCol="high_salary")
    auc = evaluator.evaluate(predictions)
    print(f"\nArea Under ROC: {auc:.4f}")
    
    spark.stop()


def decision_tree_example():
    """
    Classification with Decision Tree.
    """
    print("\n" + "="*60)
    print("3. DECISION TREE (Classification)")
    print("="*60)
    
    spark = create_spark_session()
    
    # Sample data: predict department
    data = [
        (25, 50000, 0),  # Engineering
        (30, 65000, 1),  # Sales
        (35, 75000, 0),  # Engineering
        (28, 55000, 1),  # Sales
        (32, 70000, 0),  # Engineering
        (26, 52000, 1),  # Sales
        (38, 80000, 0),  # Engineering
        (29, 58000, 1),  # Sales
    ]
    df = spark.createDataFrame(data, ["age", "salary", "department"])
    
    # Prepare features
    assembler = VectorAssembler(
        inputCols=["age", "salary"],
        outputCol="features"
    )
    feature_df = assembler.transform(df)
    
    # Split data
    train_df, test_df = feature_df.randomSplit([0.7, 0.3], seed=42)
    
    # Train model
    dt = DecisionTreeClassifier(
        featuresCol="features",
        labelCol="department",
        maxDepth=3
    )
    model = dt.fit(train_df)
    
    print(f"\nFeature importances: {model.featureImportances}")
    
    # Make predictions
    predictions = model.transform(test_df)
    
    print("\nPredictions:")
    predictions.select("age", "salary", "department", "prediction").show()
    
    # Evaluate
    evaluator = MulticlassClassificationEvaluator(
        labelCol="department",
        predictionCol="prediction",
        metricName="accuracy"
    )
    accuracy = evaluator.evaluate(predictions)
    print(f"\nAccuracy: {accuracy:.4f}")
    
    spark.stop()


def linear_regression_example():
    """
    Regression with Linear Regression.
    """
    print("\n" + "="*60)
    print("4. LINEAR REGRESSION")
    print("="*60)
    
    spark = create_spark_session()
    
    # Sample data: predict salary based on age and experience
    data = [
        (25, 2, 50000),
        (30, 5, 65000),
        (35, 10, 85000),
        (28, 3, 55000),
        (32, 7, 75000),
        (26, 2, 52000),
        (38, 12, 95000),
        (29, 4, 60000),
        (33, 8, 80000),
        (27, 3, 54000)
    ]
    df = spark.createDataFrame(data, ["age", "experience", "salary"])
    
    print("\nTraining data:")
    df.show()
    
    # Prepare features
    assembler = VectorAssembler(
        inputCols=["age", "experience"],
        outputCol="features"
    )
    feature_df = assembler.transform(df)
    
    # Split data
    train_df, test_df = feature_df.randomSplit([0.8, 0.2], seed=42)
    
    # Train model
    lr = LinearRegression(
        featuresCol="features",
        labelCol="salary",
        maxIter=10
    )
    model = lr.fit(train_df)
    
    print(f"\nCoefficients: {model.coefficients}")
    print(f"Intercept: {model.intercept}")
    print(f"RMSE: {model.summary.rootMeanSquaredError:.2f}")
    print(f"R²: {model.summary.r2:.4f}")
    
    # Make predictions
    predictions = model.transform(test_df)
    
    print("\nPredictions:")
    predictions.select("age", "experience", "salary", "prediction").show()
    
    # Evaluate
    evaluator = RegressionEvaluator(
        labelCol="salary",
        predictionCol="prediction",
        metricName="rmse"
    )
    rmse = evaluator.evaluate(predictions)
    print(f"\nTest RMSE: {rmse:.2f}")
    
    spark.stop()


def pipeline_example():
    """
    ML Pipeline for end-to-end workflow.
    """
    print("\n" + "="*60)
    print("5. ML PIPELINE")
    print("="*60)
    
    spark = create_spark_session()
    
    # Sample data
    data = [
        (1, "A", 25, 50000, 0),
        (2, "B", 30, 65000, 1),
        (3, "A", 35, 75000, 1),
        (4, "C", 28, 55000, 0),
        (5, "B", 32, 70000, 1),
        (6, "A", 26, 52000, 0),
        (7, "C", 38, 80000, 1),
        (8, "B", 29, 58000, 0)
    ]
    df = spark.createDataFrame(data, ["id", "category", "age", "salary", "label"])
    
    print("\nOriginal data:")
    df.show()
    
    # Define pipeline stages
    
    # Stage 1: Index categorical feature
    indexer = StringIndexer(
        inputCol="category",
        outputCol="category_index"
    )
    
    # Stage 2: Assemble features
    assembler = VectorAssembler(
        inputCols=["category_index", "age", "salary"],
        outputCol="features"
    )
    
    # Stage 3: Train model
    lr = LogisticRegression(
        featuresCol="features",
        labelCol="label",
        maxIter=10
    )
    
    # Create pipeline
    pipeline = Pipeline(stages=[indexer, assembler, lr])
    
    # Split data
    train_df, test_df = df.randomSplit([0.7, 0.3], seed=42)
    
    # Fit pipeline
    print("\nTraining pipeline...")
    pipeline_model = pipeline.fit(train_df)
    
    # Make predictions
    predictions = pipeline_model.transform(test_df)
    
    print("\nPredictions:")
    predictions.select("id", "category", "age", "salary", "label", "prediction").show()
    
    # Evaluate
    evaluator = BinaryClassificationEvaluator(labelCol="label")
    auc = evaluator.evaluate(predictions)
    print(f"\nAUC: {auc:.4f}")
    
    print("\n✅ Pipeline completed!")
    print("Pipeline encapsulates: StringIndexer -> VectorAssembler -> LogisticRegression")
    
    spark.stop()


# DETAILED EXPLANATION:
"""
SPARK MLLIB CONCEPTS:

1. What is MLlib?
   - Spark's machine learning library
   - Distributed ML algorithms
   - Works with DataFrames
   - Scalable to large datasets

2. Key Components:
   
   a) Transformers:
      - Transform DataFrame to another
      - Example: VectorAssembler, StringIndexer
      - Method: transform()
   
   b) Estimators:
      - Learn from data to produce model
      - Example: LogisticRegression, LinearRegression
      - Method: fit() -> Model
   
   c) Evaluators:
      - Evaluate model performance
      - Example: BinaryClassificationEvaluator
      - Method: evaluate()
   
   d) Pipeline:
      - Chain transformers and estimators
      - Simplifies workflow
      - Method: fit() -> PipelineModel

3. Feature Engineering:
   
   a) VectorAssembler:
      - Combine multiple columns into vector
      - Required for ML algorithms
      assembler = VectorAssembler(
          inputCols=["col1", "col2"],
          outputCol="features"
      )
   
   b) StringIndexer:
      - Convert categorical to numeric
      - Assigns index to each category
      indexer = StringIndexer(
          inputCol="category",
          outputCol="category_index"
      )
   
   c) StandardScaler:
      - Normalize features (mean=0, std=1)
      - Improves model performance
      scaler = StandardScaler(
          inputCol="features",
          outputCol="scaled_features"
      )
   
   d) OneHotEncoder:
      - Convert indexed categories to binary vectors
      encoder = OneHotEncoder(
          inputCol="category_index",
          outputCol="category_vec"
      )

4. Classification Algorithms:
   
   a) Logistic Regression:
      - Binary/multiclass classification
      - Linear decision boundary
      lr = LogisticRegression(
          featuresCol="features",
          labelCol="label"
      )
   
   b) Decision Tree:
      - Non-linear decision boundary
      - Interpretable
      dt = DecisionTreeClassifier(
          featuresCol="features",
          labelCol="label",
          maxDepth=5
      )
   
   c) Random Forest:
      - Ensemble of decision trees
      - More robust
      rf = RandomForestClassifier(
          featuresCol="features",
          labelCol="label",
          numTrees=100
      )
   
   d) Gradient Boosted Trees:
      - Sequential ensemble
      - High accuracy
      gbt = GBTClassifier(
          featuresCol="features",
          labelCol="label"
      )

5. Regression Algorithms:
   
   a) Linear Regression:
      - Predict continuous values
      - Linear relationship
      lr = LinearRegression(
          featuresCol="features",
          labelCol="label"
      )
   
   b) Decision Tree Regression:
      - Non-linear relationships
      dtr = DecisionTreeRegressor(
          featuresCol="features",
          labelCol="label"
      )
   
   c) Random Forest Regression:
      - Ensemble approach
      rfr = RandomForestRegressor(
          featuresCol="features",
          labelCol="label"
      )

6. Model Evaluation:
   
   a) Classification Metrics:
      - Accuracy
      - Precision, Recall, F1
      - AUC-ROC
      
      evaluator = MulticlassClassificationEvaluator(
          labelCol="label",
          predictionCol="prediction",
          metricName="accuracy"
      )
   
   b) Regression Metrics:
      - RMSE (Root Mean Squared Error)
      - MAE (Mean Absolute Error)
      - R² (R-squared)
      
      evaluator = RegressionEvaluator(
          labelCol="label",
          predictionCol="prediction",
          metricName="rmse"
      )

7. Pipeline API:
   - Chain multiple stages
   - Simplifies workflow
   - Easier to deploy
   
   pipeline = Pipeline(stages=[
       stage1,  # Transformer
       stage2,  # Transformer
       stage3   # Estimator
   ])
   
   model = pipeline.fit(train_df)
   predictions = model.transform(test_df)

8. Train-Test Split:
   
   train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

9. Cross-Validation:
   
   from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
   
   paramGrid = ParamGridBuilder() \
       .addGrid(lr.regParam, [0.1, 0.01]) \
       .addGrid(lr.maxIter, [10, 20]) \
       .build()
   
   cv = CrossValidator(
       estimator=lr,
       estimatorParamMaps=paramGrid,
       evaluator=evaluator,
       numFolds=3
   )
   
   cv_model = cv.fit(train_df)

10. Model Persistence:
    
    # Save model
    model.save("path/to/model")
    
    # Load model
    from pyspark.ml.classification import LogisticRegressionModel
    loaded_model = LogisticRegressionModel.load("path/to/model")

11. Best Practices:
    
    ✅ Always split data (train/test)
    ✅ Use Pipeline for reproducibility
    ✅ Normalize features (StandardScaler)
    ✅ Handle categorical variables (StringIndexer)
    ✅ Evaluate on test set
    ✅ Use cross-validation for tuning
    ✅ Save trained models
    
    ❌ Don't train on test data
    ❌ Don't forget feature engineering
    ❌ Don't ignore class imbalance

12. Common Workflow:
    
    # 1. Load data
    df = spark.read.csv("data.csv", header=True, inferSchema=True)
    
    # 2. Feature engineering
    indexer = StringIndexer(inputCol="category", outputCol="category_index")
    assembler = VectorAssembler(inputCols=["col1", "col2"], outputCol="features")
    
    # 3. Create model
    lr = LogisticRegression(featuresCol="features", labelCol="label")
    
    # 4. Create pipeline
    pipeline = Pipeline(stages=[indexer, assembler, lr])
    
    # 5. Split data
    train, test = df.randomSplit([0.8, 0.2])
    
    # 6. Train
    model = pipeline.fit(train)
    
    # 7. Predict
    predictions = model.transform(test)
    
    # 8. Evaluate
    evaluator = BinaryClassificationEvaluator(labelCol="label")
    auc = evaluator.evaluate(predictions)
    
    # 9. Save
    model.save("model")

MLLIB VS SCIKIT-LEARN:

MLlib:
✅ Distributed (handles big data)
✅ Integrated with Spark
✅ Scalable
❌ Fewer algorithms
❌ Less mature

Scikit-learn:
✅ More algorithms
✅ Better documentation
✅ More mature
❌ Single machine
❌ Limited scalability

Use MLlib when data doesn't fit in memory!
"""


if __name__ == '__main__':
    print("\n" + "#"*60)
    print("# APACHE SPARK - MLLIB BASICS")
    print("#"*60)
    
    feature_engineering()
    logistic_regression_example()
    decision_tree_example()
    linear_regression_example()
    pipeline_example()
    
    print("\n" + "#"*60)
    print("# ✅ ALL MLLIB EXAMPLES COMPLETED!")
    print("#"*60)
    print("\nYou now know the basics of Spark MLlib!")
