import matplotlib
try:
    matplotlib.use('Agg')
except Exception as e:
    print(f"Advertencia: No se pudo establecer el backend 'Agg'. Error: {e}")
    pass

import heapq
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#  Tren — Pesos = Nivel de Tráfico
#  (1=fluido, 5=muy congestionado)


def dijkstra_tren(red_tren, estacion_inicio):
    """
    Encuentra la ruta de MENOR DIFICULTAD/TRÁFICO
    entre la estación de inicio y todas las demás.
    """
    print(f"\n Estación de partida: {estacion_inicio}")
    print("Pesos = Nivel de tráfico (1=fluido ➜ 5=muy congestionado)\n")

    # 1. Inicialización
    dificultad = {estacion: float('inf') for estacion in red_tren}
    dificultad[estacion_inicio] = 0
    predecesores = {estacion: None for estacion in red_tren}
    cola_prioridad = [(0, estacion_inicio)]
    visitadas = set()

    print(f"Estado Inicial — Dificultad acumulada: { {k: (v if v != float('inf') else '∞') for k, v in dificultad.items()} }\n")
    print("─" * 55)

    paso = 1
    while cola_prioridad:
        dif_actual, estacion_actual = heapq.heappop(cola_prioridad)

        if estacion_actual in visitadas:
            continue

        visitadas.add(estacion_actual)

        print(f"\n🔹 PASO {paso}: Procesando ▶ {estacion_actual}  (dificultad acumulada: {dif_actual})")

        for vecina, trafico in red_tren.get(estacion_actual, []):
            nueva_dif = dif_actual + trafico
            icono = trafico_icono(trafico)

            if nueva_dif < dificultad[vecina]:
                dificultad[vecina] = nueva_dif
                predecesores[vecina] = estacion_actual
                heapq.heappush(cola_prioridad, (nueva_dif, vecina))
                print(f"  {estacion_actual} ──{icono} tráfico {trafico}──▶ {vecina}  | "
                      f"Dificultad actualizada: {nueva_dif}")
            else:
                print(f"  {estacion_actual} ──{icono} tráfico {trafico}──▶ {vecina}  | "
                      f"Sin mejora (actual: {dificultad[vecina]})")

        estado_str = {k: (v if v != float('inf') else '∞') for k, v in dificultad.items()}
        print(f" Dificultades tras paso {paso}: {estado_str}")
        print("─" * 55)
        paso += 1

    print("\n Finalizado\n")

    # Resumen de rutas óptimas
    print("  Mejores rutas desde ", estacion_inicio.center(16))
    for destino, dif in dificultad.items():
        if destino != estacion_inicio:
            ruta = reconstruir_ruta(predecesores, estacion_inicio, destino)
            print(f" {estacion_inicio} ➜ {destino}  |  Dificultad total: {dif}  |  Ruta: {' → '.join(ruta)}")

    return dificultad, predecesores


def trafico_icono(nivel):
    if nivel <= 1:   return "🟢"
    elif nivel <= 2: return "🟡"
    elif nivel <= 3: return "🟠"
    else:            return "🔴"


def reconstruir_ruta(predecesores, inicio, destino):
    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = predecesores[actual]
    ruta.reverse()
    return ruta


def dibujar_tren(red_metro, estacion_inicio, dificultad, predecesores):
    """
    Dibuja el mapa del metro con colores según tráfico y la ruta óptima resaltada.
    """
    G = nx.DiGraph()
    for u, vecinos in red_metro.items():
        for v, peso in vecinos:
            G.add_edge(u, v, weight=peso)

    pos = nx.spring_layout(G, seed=42, k=2.5)

    # Colores de nodos
    colores_nodo = []
    for nodo in G.nodes:
        if nodo == estacion_inicio:
            colores_nodo.append('#FF4500')      # Rojo — origen
        elif dificultad[nodo] == float('inf'):
            colores_nodo.append('#AAAAAA')      # Gris — no alcanzado
        else:
            colores_nodo.append('#1E90FF')      # Azul — destino alcanzado

    # Aristas de la ruta óptima
    aristas_optimas = set()
    for nodo, pred in predecesores.items():
        if pred is not None:
            aristas_optimas.add((pred, nodo))

    colores_arista = []
    anchos_arista  = []
    for u, v in G.edges():
        peso = G[u][v]['weight']
        if (u, v) in aristas_optimas:
            colores_arista.append('#00CC44')    # Verde — ruta óptima
            anchos_arista.append(4)
        else:
            # Color según tráfico
            if peso <= 1:   color = '#90EE90'
            elif peso <= 2: color = '#FFD700'
            elif peso <= 3: color = '#FFA500'
            else:           color = '#FF6347'
            colores_arista.append(color)
            anchos_arista.append(1.5)

    # Etiquetas de nodos con dificultad
    etiquetas = {
        n: f"{n}\nD:{dificultad[n] if dificultad[n] != float('inf') else '∞'}"
        for n in G.nodes
    }

    # Dibujar gráfico
    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')

    plt.title(f" Tren — Ruta de Menor Tráfico  (Salida: {estacion_inicio})",
              fontsize=15, fontweight='bold', color='white', pad=15)

    nx.draw_networkx_nodes(G, pos, node_color=colores_nodo, node_size=2200, ax=ax, alpha=0.95)
    nx.draw_networkx_edges(G, pos, edge_color=colores_arista, width=anchos_arista,
                           arrows=True, arrowsize=20,
                           connectionstyle='arc3,rad=0.1', ax=ax)
    nx.draw_networkx_labels(G, pos, labels=etiquetas, font_size=9,
                            font_color='white', font_weight='bold', ax=ax)

    pesos_arista = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos_arista,
                                 font_color='yellow', font_size=8, ax=ax)

    # Leyenda
    leyenda = [
        mpatches.Patch(color='#FF4500', label='Estación de salida'),
        mpatches.Patch(color='#1E90FF', label='Estación alcanzada'),
        mpatches.Patch(color='#00CC44', label='Ruta óptima (menor tráfico)'),
        mpatches.Patch(color='#90EE90', label='Tráfico 1 — Fluido'),
        mpatches.Patch(color='#FFD700', label='Tráfico 2 — Ligero'),
        mpatches.Patch(color='#FFA500', label='Tráfico 3 — Moderado'),
        mpatches.Patch(color='#FF6347', label='Tráfico 4-5 — Congestionado'),
    ]
    ax.legend(handles=leyenda, loc='lower left', facecolor='#2a2a4a',
              edgecolor='white', labelcolor='white', fontsize=8.5)

    plt.axis('off')
    output_file = "Tren_Resultado.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n Gráfico guardado en: {output_file}")
    return output_file


# Configuración

if __name__ == "__main__":

    # Estaciones y conexiones con nivel de tráfico (1=fluido, 5=muy congestionado)
    red_tren = {
        'Central':      [('Norte',    2), ('Sur',     3)],
        'Norte':        [('Este',     1), ('Aeropuerto', 4)],
        'Sur':          [('Oeste',    2), ('Universidad', 1)],
        'Este':         [('Aeropuerto', 2), ('Universidad', 3)],
        'Oeste':        [('Central',  4), ('Universidad', 2)],
        'Universidad':  [('Aeropuerto', 5)],
        'Aeropuerto':   []
    }

    estacion_inicio = 'Central'

    # 1. Ejecutar Dijkstra con salida en consola
    dificultad, predecesores = dijkstra_tren(red_tren, estacion_inicio)

    # 2. Generar gráfico
    print("\n Generando mapa del tren...")
    archivo = dibujar_tren(red_tren, estacion_inicio, dificultad, predecesores)

    print("\n Proceso finalizado, muchas gracias")
    print(f"   Archivo gráfico: {archivo}\n")