import org.apache.spark.sql.SparkSession

object DataFrameVsDataset {

  // Case class gives Dataset its strongly typed structure
  case class Employee(
                       id: Int,
                       name: String,
                       salary: Double
                     )

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder()
      .appName("DataFrameVsDataset")
      .master("local[*]")
      .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    import spark.implicits._

    // =====================================================
    // 1. DATAFRAME EXAMPLE
    // =====================================================

    val df = Seq(
      (1, "John", 80000.0),
      (2, "Mary", 70000.0),
      (3, "David", 90000.0)
    ).toDF("id", "name", "salary")

    println("----- DataFrame -----")

    df.show()

    // Correct
    df.select("name", "salary").show()


    // Uncomment this line:
    //
    // df.select("salry").show()
    //
    // "salry" is misspelled.
    //
    // Scala compiler sees "salry" as just a String,
    // so the code can compile.
    //
    // Spark detects the invalid column during analysis/runtime.
    //
    // This demonstrates weaker compile-time type safety.


    // =====================================================
    // 2. DATASET EXAMPLE
    // =====================================================

    val ds = Seq(
      Employee(1, "John", 80000.0),
      Employee(2, "Mary", 70000.0),
      Employee(3, "David", 90000.0)
    ).toDS()

    println("----- Dataset -----")

    ds.show()

    // Correct
    val salaries = ds.map(emp => emp.salary)

    salaries.show()


    // Uncomment this line:
    //
    // val wrong = ds.map(emp => emp.salry)
    //
    // "salry" doesn't exist in Employee.
    //
    // Scala compiler knows emp is an Employee,
    // so this FAILS AT COMPILE TIME.


    // =====================================================
    // 3. DATASET TYPE SAFETY
    // =====================================================

    val highSalaryEmployees =
      ds.filter(emp => emp.salary > 75000.0)

    println("----- Salary > 75000 -----")

    highSalaryEmployees.show()


    // Uncomment:
    //
    // ds.filter(emp => emp.salary > "75000")
    //
    // salary is Double
    // "75000" is String
    //
    // The compiler catches the incompatible types.


    spark.stop()
  }
}