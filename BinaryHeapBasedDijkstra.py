import heapq
import time
import psutil
import os
import statistics
from collections import defaultdict, defaultdict

def dijkstra(graph, start, end):
    queue = [(0, start, [])]
    visited = set()
    min_dist = {start: 0}

    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]

        if node == end:
            return cost, path

        for neighbor, weight in graph[node]:
            if neighbor in visited:
                continue
            prev = min_dist.get(neighbor, float('inf'))
            next_cost = cost + weight
            if next_cost < prev:
                min_dist[neighbor] = next_cost
                heapq.heappush(queue, (next_cost, neighbor, path))

    return float('inf'), []

def read_edges(filename, limit=None):
    edges = []
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            parts = line.strip().split()
            if len(parts) == 3:
                u, v, w = parts
                edges.append((u, v, float(w)))
    return edges

def build_graph(edges):
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))  # undirected
    return graph

def measure_performance(filename, start_node, end_node, sample_sizes, repetitions=5):
    all_results = defaultdict(list)  # sample_size -> list of results

    for size in sample_sizes:
        for _ in range(repetitions):
            edges = read_edges(filename, limit=size)
            graph = build_graph(edges)

            num_vertices = len(graph)
            num_edges = sum(len(neighbors) for neighbors in graph.values()) // 2

            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / 1024 / 1024

            start_time = time.time()
            distance, path = dijkstra(graph, start_node, end_node)
            end_time = time.time()

            mem_after = process.memory_info().rss / 1024 / 1024

            all_results[size if size is not None else 'ALL'].append({
                'distance': distance,
                'path': path,
                'execution_time_sec': end_time - start_time,
                'memory_usage_mb': mem_after - mem_before,
                'num_vertices': num_vertices,
                'num_edges': num_edges
            })

    return all_results

if __name__ == "__main__":
    filename = 'random_16_16_256_final.txt'
    start_node = 'v4.8.64'
    end_node = 'v8.4.96'
    sample_sizes = [1, 1000, 2000, 5000, 7000, 10000, 20000, 50000, 70000, 100000, 150000, 200000, 250000, None]
    repetitions = 5  # puedes aumentar si quieres mejor precisión

    performance_results = measure_performance(filename, start_node, end_node, sample_sizes, repetitions)

    for size, results in performance_results.items():
        times = [r['execution_time_sec'] for r in results]
        mems = [r['memory_usage_mb'] for r in results]
        vertices = [r['num_vertices'] for r in results]
        edges = [r['num_edges'] for r in results]

        print(f"\n=== Estadísticas para sample_size = {size} ({repetitions} repeticiones) ===")
        print(f"Tiempo (segundos) -> Min: {min(times):.6f}, Max: {max(times):.6f}, Media: {statistics.mean(times):.6f}, Mediana: {statistics.median(times):.6f}, Stdev: {statistics.stdev(times):.6f}, Var: {statistics.variance(times):.6f}")
        print(f"Memoria (MB)     -> Min: {min(mems):.2f}, Max: {max(mems):.2f}, Media: {statistics.mean(mems):.2f}")
        print(f"Vértices         -> Promedio: {statistics.mean(vertices):.2f}")
        print(f"Aristas          -> Promedio: {statistics.mean(edges):.2f}")
