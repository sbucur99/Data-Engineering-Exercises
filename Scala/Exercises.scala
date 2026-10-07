import scala.util.Try

object ScalaFundamentalsExercise {

  def main(args: Array[String]): Unit = {

    // ============================================================
    // Task 1 - Collections and Transformation Thinking
    // ============================================================

    // Create a List of employee salaries
    val salaries = List(60000, 75000, 82000, 90000, 100000)

    // Apply a 10% increase
    val updatedSalaries = salaries.map(salary => salary * 1.10)

    // Keep salaries greater than 80,000
    val highSalaries = updatedSalaries.filter(salary => salary > 80000)

    println("Task 1")
    println(s"Original salaries: $salaries")
    println(s"Updated salaries: $updatedSalaries")
    println(s"Salaries greater than 80,000: $highSalaries")

    // Set automatically removes duplicates
    val departments = Set(
      "Engineering",
      "HR",
      "Finance",
      "Engineering",
      "Sales",
      "HR"
    )

    println(s"Departments with duplicates removed: $departments")

    // Map: employee ID -> department
    val employeeDepartments = Map(
      101 -> "Engineering",
      102 -> "Finance",
      103 -> "HR"
    )
    //    print(employeeDepartments.size)   // length for list or size for list

    for (i <- employeeDepartments) {
      //      employeeDepartments.
    }
    // Safe retrieval using get
    println(s"Employee 101 department: ${employeeDepartments.get(101)}")
    println(s"Employee 999 department: ${employeeDepartments.get(999)}")


    // ============================================================
    // Task 2 - Pattern Matching
    // ============================================================

    def classifyDepartment(department: String): String = {
      department match {
        case "Engineering" => "Technical"
        case "HR" => "Corporate"
        case "Finance" => "Business"
        case "Legal" => "Corporate"
        case "Sales" => "Revenue"
        case _ => "Unknown"
      }
    }

    val departmentList = List(
      "Engineering",
      "HR",
      "Finance",
      "Legal",
      "Sales",
      "Marketing"
    )

    val classifications = departmentList.map(department =>
      (department, classifyDepartment(department))
    )

    println("\nTask 2")

    classifications.foreach {
      case (department, category) =>
        println(s"$department -> $category")
    }


    // ============================================================
    // Task 3 - Null Safety with Option
    // ============================================================

    val salaryData = List(
      Some(75000),
      None,
      Some(90000),
      Some(65000),
      None
    )

    // Replace None with 0
    val salariesWithDefaults = salaryData.map(
      salary => salary.getOrElse(0)
    )

    println("\nTask 3")
    println(s"Original salary data: $salaryData")
    println(s"Missing salaries replaced with 0: $salariesWithDefaults")

    /*
      Option is preferable to null because it explicitly represents
      whether a value exists.
      This reduces NullPointerException risk.
      It also forces developers to handle missing values explicitly.
      This makes data pipelines safer and easier to reason about.
    */


    // ============================================================
    // Task 4 - Reusable Validation with Traits
    // ============================================================

    trait Validator {
      def validateSalary(salary: Int): Boolean
    }

    class EmployeeValidator extends Validator {

      override def validateSalary(salary: Int): Boolean = {
        salary > 0
      }
    }

    val validator = new EmployeeValidator()

    val testSalaries = List(50000, 0, -10000)

    println("\nTask 4")

    testSalaries.foreach { salary =>
      println(s"Salary $salary valid: ${validator.validateSalary(salary)}")
    }


    // ============================================================
    // Task 5 - Safe Parsing with Try
    // ============================================================

    val rawValues = List(
      "10",
      "20",
      "abc",
      "40",
      "not_available"
    )

    // Try safely attempts the conversion.
    // Invalid values become Failure instead of terminating the program.
    val parsedValues = rawValues.map(value => Try(value.toInt))

    //    println("Types:")
    //    var parsedValues = rawValues.map(value => Try(value.toInt).isSuccess)

    //   parsedValues.foreach(value => println(value.getClass))
    //    parsedValues.foreach(value => println(value))

    //    print()

    // Keep only successfully parsed integers
    val validValues = parsedValues.collect {
      case scala.util.Success(value) => value
    }

    // Count failures
    val invalidCount = parsedValues.count {
      case scala.util.Failure(_) => true
      case scala.util.Success(_) => false
    }

    println("\nTask 5")
    println(s"Raw values: $rawValues")
    println(s"Cleaned values: $validValues")
    println(s"Invalid input count: $invalidCount")


    // ------------------------------------------------------------
    // Task 6 - Mini Pipeline
    // ------------------------------------------------------------

    case class Employee(
       id: Int,
       name: String,
       dept: String,
       salary: Double
     )

    // Raw input
    val rawEmployees = List(
      ("1", "Alice", "Engineering", "85000"),
      ("2", "Bob", "Engineering", "72000"),
      ("3", "Charlie", "Sales", "65000"),
      ("4", "Diana", "Sales", "90000"),
      ("5", "Evan", "HR", "invalid"),
      ("6", "Frank", "", "78000"),
      ("7", "Grace", "HR", "71000")
    )

    // Clean and safely parse the input
    val employees = rawEmployees.flatMap {
      case (id, name, dept, salary) =>
        for {
          parsedId <- Try(id.toInt).toOption
          parsedSalary <- Try(salary.toDouble).toOption
          if name.nonEmpty
          if dept.nonEmpty
        } yield Employee(parsedId, name, dept, parsedSalary)
    }

    // Keep employees with salary > 70,000
    val highEarners = employees.filter(_.salary > 70000)

    // Group by department
    val grouped = highEarners.groupBy(_.dept)

    // Calculate employee count, total salary, and average salary
    val summary = grouped.map {
      case (dept, employees) =>
        val employeeCount = employees.size
        val totalSalary = employees.map(_.salary).sum
        val averageSalary = totalSalary / employeeCount

        (dept, employeeCount, totalSalary, averageSalary)
    }

    println("Task 6")
    println("\nCleaned employees:")
    employees.foreach(println)

    println("\nEmployees with salary > 70,000:")
    highEarners.foreach(println)

    println("\nDepartment summary:")
    summary.foreach {
      case (dept, count, total, average) =>
        println(
          f"$dept%-15s Count: $count%-3d Total: $$${total}%.2f Average: $$${average}%.2f"
        )
    }
  }
}