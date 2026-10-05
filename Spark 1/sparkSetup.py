# NOTE : Did in jupyter notebook docker
import pyspark 
from pyspark.sql import SparkSession 
spark = SparkSession.builder \
    .appName("AdvancedSparkTraining") \
    .master("local[*]") \
    .getOrCreate()


df = spark.read.csv("orders.csv", header=True, inferSchema=True) 
df.filter(df.price > 100).show()

df.filter(df.price > 100).explain(True) 

df.groupBy("city").sum("price").explain(True) 

df.cache()

df.show()

df.groupBy("city").sum("price").explain() 

df.filter("price > 100").explain()

customers = spark.read.csv( 
"customers.csv", 
header=True, 
inferSchema=True 
) 

df.join(customers, "customer_id").explain(True)

spark.conf.set("spark.sql.adaptive.enabled", "true") 

products = spark.read.csv( 
"products.csv", 
header=True, 
inferSchema=True 
) 

df = df.join(customers,"customer_id") \
    .join(products,"product_id")

df.groupBy("city").sum("price")

df.groupBy("customer_id") \
.sum("price") \
.orderBy("sum(price)", ascending=False)

df.write.parquet("output/sales_summary")