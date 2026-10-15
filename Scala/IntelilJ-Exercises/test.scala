package com.spark.test

import org.apache.spark.sql.SparkSession

object test {
  def main(args: Array[String]): Unit = {
    // 1. Initialize the local Spark Session
    val spark = SparkSession.builder()
      .appName("Spark4Validation")
      .master("local[*]") // Uses all available CPU cores on your machine
      .getOrCreate()

    println("\n" + "=" * 50)
    println("🚀 SUCCESS: Apache Spark 4.2.0 is up and running!")
    println(s"Scala Version: ${util.Properties.versionNumberString}")
    println("=" * 50 + "\n")

    // 2. Create a tiny test DataFrame
    import spark.implicits._
    val sampleData = Seq(
      (1, "Spark 4.2.0 Working", true),
      (2, "JDK 25 Compatible", true)
    )
    val df = sampleData.toDF("ID", "Status_Message", "Is_Active")

    // 3. Print the DataFrame layout to the console
    df.show()

    // 4. Safely stop the Spark engine
    spark.stop()
  }
}