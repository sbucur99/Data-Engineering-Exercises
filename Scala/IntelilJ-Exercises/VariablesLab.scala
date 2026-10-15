object VariablesLab extends App {

  val company = "DataPlatform"
  var engineers = 5

  val age: Int = 30
//  val salary: Double = 90000.50
//  val isActive: Boolean = true

//  print("Age:"+age)

//  val name = "Data"
//  val role = name + " Engineer"

//  print(role)



  val name = "Alice"
  val salary = 90000
//
//  println(s"$name earns $salary")

//  println(f"Salary = $salary%.2f")

//  val result =
//    if(age > 18) "Adult"
//    else "Minor"
//  print(result)

//  for(i <- 1 to 20) {
//    if (i % 3 == 0) println(i)
//  }

//  def add(a: Int, b: Int): (Int, Int, Int) = {
//    (a + b,
//    a + 5,
//    a - b)
//  }
//  println(add(2,3))


//  var counter = 0
//
//  def increment(): Int = {
//    counter += 1
//    counter
//  }
//
//  println(increment())
//  println(increment())


//  var numbers = List(List(1,2,3), List(1,2,3,4,5))
//
////  var doubled = numbers.flatMap(x => List(x * 2))
//
//  val doubled = numbers.map(x => x.map(y => y * 2))
//
//  var doubled2 = numbers.flatMap(x => x.map(y => y * 2))
//  println(doubled)
//  println(doubled2)


//  var ls = List(1,2,3)
//
//  println(ls.reduce(_ + _))
////  println()

//  val employees = Map(
//    1 -> "Alice",
//    2 -> "Bob",
//    3 -> "Charlie"
//  )
//  println(employees(2))


//  val record = (1, "Alice", 90000)
//
////  print(record._1)
//
////  print(record._1)
//
//  record.productIterator.foreach(x => println(x))

// For schema enforcement
  case class Employee(id:Int,name:String,salary:Int)

  val employees = List(
    Employee(1,"Alice",90000),
    Employee(2,"Bob",75000),
    Employee(3,"Charlie",60000)
  )

  val highSalary =
    employees.filter(e => e.salary > 80000)

  println(highSalary)








  //  val record = List(1, "Alice", 90000)
//  print(record(0))

  //  println(company)
//  println(engineers)

//  engineers = engineers + 3

//  println(engineers)

}