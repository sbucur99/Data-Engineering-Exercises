import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object InClassLab extends App {

  val spark = SparkSession.builder().appName("EmployeePipeline").master("local[*]").getOrCreate()

  spark.sparkContext.setLogLevel("ERROR")

  import spark.implicits._

  var listi = List(1, 2, 3, 4, 5).toDS()

  import org.apache.spark.sql.types._
  val schema = StructType(List(
    StructField("emp_id", IntegerType, true),
    StructField("name", StringType, true),
    StructField("department", StringType, true),
    StructField("city", StringType, true),
    StructField("salary", StringType, true),
    StructField("bonus", IntegerType, true),
    StructField("experience", IntegerType, true),
    StructField("join_year", IntegerType, true)
  ))

  val df = spark.read
    .option("header","true")
    .schema(schema)
    .csv("employee_transactions.csv")

  case class Employee (emp_id: Int, name: String, department: String, city: String, salary: String, bonus: Int, experience: Int, join_year: Int)

  val dataSet = df.as[Employee]

  val dataSet2 = dataSet

  val groupedDataSet = dataSet.groupBy("department").agg(sum("salary"))

  println("HEREEEEEEEEEEEEEE")
  groupedDataSet.show()

  //  df.show()
  //  df.printSchema()
  //  df.head(5).foreach(println)
  //  println(df.count())

  val cleanedSalary = df.withColumn("salary",
    when(col("salary").rlike("[0-9]+"),
      col("salary").cast("int"))
      .otherwise(null)
  )
  //  cleanedSalary.show()

  val cleaned = cleanedSalary
    .filter(col("salary").isNotNull)
    .filter(col("department").isNotNull)
    .filter(col("name").isNotNull)

  //  cleaned.show()

  val bonusFixed = cleaned.withColumn("bonus",
    coalesce(col("bonus"),lit(0)) )

  //  bonusFixed.show()

  val enriched = bonusFixed.withColumn("total_compensation",
    col("salary") + col("bonus")
  )

  //  enriched.show()

  val withLevel = enriched.withColumn( "seniority",
    when(col("experience") >= 8,"Senior")
      .when(col("experience") >=5,"Mid")
      .otherwise("Junior")
  )

  //  withLevel.show()

  //  withLevel.select(
  //    "name", "salary", "bonus", "total_compensation", "seniority"
  //  ).show()

  val deptMetrics = withLevel.groupBy("department")
    .agg(
      count("*").alias("employee_count"),
      sum("salary").alias("total_salary"),
      avg("salary").alias("avg_salary")
    )

  //  deptMetrics.show()

  val anything = withLevel.groupBy("city").agg(avg("salary").alias("average_by_city"))
  //  anything.show()

  val topPaid = withLevel.orderBy(col("salary").desc).limit(3)
  //  topPaid.show()
}

 