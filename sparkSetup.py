# NOTE : Did in jupyter notebook docker
import pyspark 
from pyspark.sql import SparkSession 
spark = SparkSession.builder \
    .appName("AdvancedSparkTraining") \
    .master("local[*]") \
    .getOrCreate()


df = spark.read.csv("orders.csv", header=True, inferSchema=True) 
df.filter(df.price > 100).show()
"""
+--------+-----------+----------+--------+-----+
|order_id|customer_id|product_id|    city|price|
+--------+-----------+----------+--------+-----+
|       1|        101|        P1|New York|  200|
|       2|        102|        P2| Chicago|  300|
|       3|        101|        P3|New York|  150|
|       4|        103|        P2|  Dallas|  400|
|       5|        104|        P4| Chicago|  250|
|       6|        105|        P1|New York|  350|
|       7|        101|        P2|  Dallas|  500|
|       9|        103|        P4|New York|  600|
|      10|        105|        P1| Chicago|  450|
+--------+-----------+----------+--------+-----+
"""

df.filter(df.price > 100).explain(True) 
"""
== Parsed Logical Plan ==
Filter (price#21 > 100)
+- Relation [order_id#17,customer_id#18,product_id#19,city#20,price#21] csv

== Analyzed Logical Plan ==
order_id: int, customer_id: int, product_id: string, city: string, price: int
Filter (price#21 > 100)
+- Relation [order_id#17,customer_id#18,product_id#19,city#20,price#21] csv

== Optimized Logical Plan ==
Filter (isnotnull(price#21) AND (price#21 > 100))
+- Relation [order_id#17,customer_id#18,product_id#19,city#20,price#21] csv

== Physical Plan ==
*(1) Filter (isnotnull(price#21) AND (price#21 > 100))
+- FileScan csv [order_id#17,customer_id#18,product_id#19,city#20,price#21] Batched: false, DataFilters: [isnotnull(price#21), (price#21 > 100)], Format: CSV, Location: InMemoryFileIndex(1 paths)[file:/home/jovyan/orders.csv], PartitionFilters: [], PushedFilters: [IsNotNull(price), GreaterThan(price,100)], ReadSchema: struct<order_id:int,customer_id:int,product_id:string,city:string,price:int>

Selection deleted

"""


df.groupBy("city").sum("price").explain(True) 
"""
== Parsed Logical Plan ==
'Aggregate ['city], ['city, sum(price#21) AS sum(price)#60L]
+- Relation [order_id#17,customer_id#18,product_id#19,city#20,price#21] csv

== Analyzed Logical Plan ==
city: string, sum(price): bigint
Aggregate [city#20], [city#20, sum(price#21) AS sum(price)#60L]
+- Relation [order_id#17,customer_id#18,product_id#19,city#20,price#21] csv

== Optimized Logical Plan ==
Aggregate [city#20], [city#20, sum(price#21) AS sum(price)#60L]
+- Project [city#20, price#21]
   +- Relation [order_id#17,customer_id#18,product_id#19,city#20,price#21] csv

== Physical Plan ==
AdaptiveSparkPlan isFinalPlan=false
+- HashAggregate(keys=[city#20], functions=[sum(price#21)], output=[city#20, sum(price)#60L])
   +- Exchange hashpartitioning(city#20, 200), ENSURE_REQUIREMENTS, [plan_id=75]
      +- HashAggregate(keys=[city#20], functions=[partial_sum(price#21)], output=[city#20, sum#64L])
         +- FileScan csv [city#20,price#21] Batched: false, DataFilters: [], Format: CSV, Location: InMemoryFileIndex(1 paths)[file:/home/jovyan/orders.csv], PartitionFilters: [], PushedFilters: [], ReadSchema: struct<city:string,price:int>

"""
df.cache()
# DataFrame[order_id: int, customer_id: int, product_id: string, city: string, price: int]

df.show()
"""
+--------+-----------+----------+--------+-----+
|order_id|customer_id|product_id|    city|price|
+--------+-----------+----------+--------+-----+
|       1|        101|        P1|New York|  200|
|       2|        102|        P2| Chicago|  300|
|       3|        101|        P3|New York|  150|
|       4|        103|        P2|  Dallas|  400|
|       5|        104|        P4| Chicago|  250|
|       6|        105|        P1|New York|  350|
|       7|        101|        P2|  Dallas|  500|
|       8|        102|        P3| Chicago|  100|
|       9|        103|        P4|New York|  600|
|      10|        105|        P1| Chicago|  450|
+--------+-----------+----------+--------+-----+

"""

df.groupBy("city").sum("price").explain() 
"""
== Physical Plan ==
AdaptiveSparkPlan isFinalPlan=false
+- HashAggregate(keys=[city#20], functions=[sum(price#21)])
   +- Exchange hashpartitioning(city#20, 200), ENSURE_REQUIREMENTS, [plan_id=108]
      +- HashAggregate(keys=[city#20], functions=[partial_sum(price#21)])
         +- InMemoryTableScan [city#20, price#21]
               +- InMemoryRelation [order_id#17, customer_id#18, product_id#19, city#20, price#21], StorageLevel(disk, memory, deserialized, 1 replicas)
                     +- FileScan csv [order_id#17,customer_id#18,product_id#19,city#20,price#21] Batched: false, DataFilters: [], Format: CSV, Location: InMemoryFileIndex(1 paths)[file:/home/jovyan/orders.csv], PartitionFilters: [], PushedFilters: [], ReadSchema: struct<order_id:int,customer_id:int,product_id:string,city:string,price:int>

"""

df.filter("price > 100").explain()
"""
== Physical Plan ==
AdaptiveSparkPlan isFinalPlan=false
+- Filter (isnotnull(price#21) AND (price#21 > 100))
   +- InMemoryTableScan [order_id#17, customer_id#18, product_id#19, city#20, price#21], [isnotnull(price#21), (price#21 > 100)]
         +- InMemoryRelation [order_id#17, customer_id#18, product_id#19, city#20, price#21], StorageLevel(disk, memory, deserialized, 1 replicas)
               +- FileScan csv [order_id#17,customer_id#18,product_id#19,city#20,price#21] Batched: false, DataFilters: [], Format: CSV, Location: InMemoryFileIndex(1 paths)[file:/home/jovyan/orders.csv], PartitionFilters: [], PushedFilters: [], ReadSchema: struct<order_id:int,customer_id:int,product_id:string,city:string,price:int>

"""

customers = spark.read.csv( 
"customers.csv", 
header=True, 
inferSchema=True 
) 

df.join(customers, "customer_id").explain(True)
"""
== Parsed Logical Plan ==
'Join UsingJoin(Inner, [customer_id])
:- Relation [order_id#17,customer_id#18,product_id#19,city#20,price#21] csv
+- Relation [customer_id#394,name#395,segment#396] csv

== Analyzed Logical Plan ==
customer_id: int, order_id: int, product_id: string, city: string, price: int, name: string, segment: string
Project [customer_id#18, order_id#17, product_id#19, city#20, price#21, name#395, segment#396]
+- Join Inner, (customer_id#18 = customer_id#394)
   :- Relation [order_id#17,customer_id#18,product_id#19,city#20,price#21] csv
   +- Relation [customer_id#394,name#395,segment#396] csv

== Optimized Logical Plan ==
Project [customer_id#18, order_id#17, product_id#19, city#20, price#21, name#395, segment#396]
+- Join Inner, (customer_id#18 = customer_id#394)
   :- Filter isnotnull(customer_id#18)
   :  +- InMemoryRelation [order_id#17, customer_id#18, product_id#19, city#20, price#21], StorageLevel(disk, memory, deserialized, 1 replicas)
   :        +- FileScan csv [order_id#17,customer_id#18,product_id#19,city#20,price#21] Batched: false, DataFilters: [], Format: CSV, Location: InMemoryFileIndex(1 paths)[file:/home/jovyan/orders.csv], PartitionFilters: [], PushedFilters: [], ReadSchema: struct<order_id:int,customer_id:int,product_id:string,city:string,price:int>
   +- Filter isnotnull(customer_id#394)
      +- Relation [customer_id#394,name#395,segment#396] csv

== Physical Plan ==
AdaptiveSparkPlan isFinalPlan=false
+- Project [customer_id#18, order_id#17, product_id#19, city#20, price#21, name#395, segment#396]
   +- BroadcastHashJoin [customer_id#18], [customer_id#394], Inner, BuildRight, false
      :- Filter isnotnull(customer_id#18)
      :  +- InMemoryTableScan [order_id#17, customer_id#18, product_id#19, city#20, price#21], [isnotnull(customer_id#18)]
      :        +- InMemoryRelation [order_id#17, customer_id#18, product_id#19, city#20, price#21], StorageLevel(disk, memory, deserialized, 1 replicas)
      :              +- FileScan csv [order_id#17,customer_id#18,product_id#19,city#20,price#21] Batched: false, DataFilters: [], Format: CSV, Location: InMemoryFileIndex(1 paths)[file:/home/jovyan/orders.csv], PartitionFilters: [], PushedFilters: [], ReadSchema: struct<order_id:int,customer_id:int,product_id:string,city:string,price:int>
      +- BroadcastExchange HashedRelationBroadcastMode(List(cast(input[0, int, false] as bigint)),false), [plan_id=243]
         +- Filter isnotnull(customer_id#394)
            +- FileScan csv [customer_id#394,name#395,segment#396] Batched: false, DataFilters: [isnotnull(customer_id#394)], Format: CSV, Location: InMemoryFileIndex(1 paths)[file:/home/jovyan/customers.csv], PartitionFilters: [], PushedFilters: [IsNotNull(customer_id)], ReadSchema: struct<customer_id:int,name:string,segment:string>

"""

spark.conf.set("spark.sql.adaptive.enabled", "true") 

products = spark.read.csv( 
"products.csv", 
header=True, 
inferSchema=True 
) 

df = df.join(customers,"customer_id") \
    .join(products,"product_id")

df.groupBy("city").sum("price")
# DataFrame[city: string, sum(price): bigint]

df.groupBy("customer_id") \
.sum("price") \
.orderBy("sum(price)", ascending=False)
# DataFrame[customer_id: int, sum(price): bigint]

df.write.parquet("output/sales_summary")