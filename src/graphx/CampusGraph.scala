
import org.apache.spark.sql.SparkSession
import org.apache.spark.graphx._
import org.apache.spark.rdd.RDD

object CampusGraph {

  def main(args: Array[String]): Unit = {

    // 1. Create Spark Session
    val spark = SparkSession.builder()
      .appName("CampusFlow GraphX")
      .master("local[*]")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    // 2. Read campus CSV files
    val stops = spark.read
      .option("header", "true")
      .option("inferSchema", "true")
      .csv("data/raw/stops.csv")

    val routeStops = spark.read
      .option("header", "true")
      .option("inferSchema", "true")
      .csv("data/raw/route_stops.csv")

    // 3. Create vertices
    // ST01 becomes vertex ID 1, ST02 becomes 2, etc.
    val vertices: RDD[(VertexId, String)] =
      stops.rdd.map { row =>
        val stopId = row.getAs[String]("stop_id")
        val stopName = row.getAs[String]("stop_name")
        val numericId = stopId.drop(2).toLong

        (numericId, stopName)
      }

    // 4. Order stops within each route
    val orderedStops = routeStops.rdd
      .map { row =>
        (
          row.getAs[String]("route_id"),
          (
            row.getAs[Int]("stop_sequence"),
            row.getAs[String]("stop_id"),
            row.getAs[Double]("distance_from_previous_km")
          )
        )
      }
      .groupByKey()
      .flatMap { case (routeId, stopsInRoute) =>

        val sorted = stopsInRoute.toSeq.sortBy(_._1)

        // Connect each stop to the next stop
        sorted.sliding(2).collect {
          case Seq(previous, next) =>
            (
              previous._2,
              next._2,
              routeId,
              next._3
            )
        }
      }

    // 5. Create directed edges
    val edges: RDD[Edge[String]] =
      orderedStops.map {
        case (source, destination, routeId, distance) =>

          val sourceId = source.drop(2).toLong
          val destinationId = destination.drop(2).toLong

          Edge(
            sourceId,
            destinationId,
            s"$routeId|$distance"
          )
      }

    // 6. Build GraphX graph
    val graph: Graph[String, String] =
      Graph(vertices, edges)

    // 7. Display graph information
    println("\n========== CAMPUSFLOW GRAPHX ==========")

    println(s"Total vertices (stops): ${graph.vertices.count()}")
    println(s"Total edges (connections): ${graph.edges.count()}")

    println("\nVertices:")
    graph.vertices.collect().sortBy(_._1).foreach(println)

    
    println("\nEdges:")
    graph.edges.collect().foreach(println)

    // 8. Calculate vertex degrees
    val inDegrees = graph.inDegrees
    val outDegrees = graph.outDegrees
    val totalDegrees = graph.degrees

    println("\n========== STOP DEGREE ANALYSIS ==========")

    val degreeAnalysis = graph.vertices
    .leftOuterJoin(inDegrees)
    .leftOuterJoin(outDegrees)
    .leftOuterJoin(totalDegrees)
    .map {
        case (id, (((name, in), out), total)) =>
        (
            id,
            name,
            in.getOrElse(0),
            out.getOrElse(0),
            total.getOrElse(0)
        )
    }
    .sortBy(_._1)

    degreeAnalysis.collect().foreach(println)

    // 9. Find the stop with the highest total degree
    val mostConnected = degreeAnalysis
    .max()(Ordering.by(_._5))

    println("\nMost connected stop:")
    println(mostConnected)


    // 10. Connected Components Analysis

    println("\n========== CONNECTED COMPONENTS ==========")

    val components = graph.connectedComponents()

    val componentResults = graph.vertices
    .join(components.vertices)
    .map {
        case (vertexId, (stopName, componentId)) =>
        (componentId, stopName)
    }
    .sortBy(_._1)

    componentResults.collect().foreach(println)

    // Count the number of unique components
    val totalComponents = components.vertices
    .map(_._2)
    .distinct()
    .count()

    println(s"\nTotal connected components: $totalComponents")


    // 11. PageRank Analysis

    println("\n========== PAGERANK ANALYSIS ==========")

    val pageRankGraph = graph.pageRank(0.0001)

    val pageRankResults = pageRankGraph.vertices
    .join(graph.vertices)
    .map {
        case (vertexId, (rank, stopName)) =>
        (stopName, rank)
    }
    .sortBy(_._2, ascending = false)

    pageRankResults.collect().foreach(println)

    println("\nMost important stop according to PageRank:")
    println(pageRankResults.first())



    spark.stop()

  }
}
