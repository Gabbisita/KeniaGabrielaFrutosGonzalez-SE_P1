import heapq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import os


def prim_wifi_campus(campus_torres, pos_torres, torre_inicio):

    # 1. Carpeta de salida para los pasos
    output_dir = "pasos_wifi"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"\n Pesos = Consumo de energía entre torres (kWh)")
    print(f" Torre de inicio: {torre_inicio}")
    print(f" Imágenes paso a paso en: '{output_dir}/'\n")
    print("─" * 56)

    # 2. Construir grafo NetworkX para visualización
    G = nx.Graph()
    for torre in campus_torres:
        for vecina, energia in campus_torres[torre]:
            if torre < vecina:
                G.add_edge(torre, vecina, weight=energia)
        if torre not in G.nodes():
            G.add_node(torre)

    # Tipo de zona por torre
    tipo_zona = {
        'Biblioteca':       'academico',
        'GOE':         'academico',
        'Aulas L':          'academico',
        'Aulas G':          'academico',
        'Lab. Cómputo':     'lab',
        'Lab. Ingeniería':    'lab',
        'Cafetería':        'social',
        'Gimnasio':         'social',
        'Auditorio':          'social',
    }

    def color_nodo(torre, visitados):
        if torre == torre_inicio and torre in visitados:
            return '#FF4500'           # Naranja — torre origen
        if torre in visitados:
            return '#2a9d8f'           # Verde azulado — conectada
        return '#adb5bd'               # Gris — pendiente

    # 3. Función de dibujo
    paso_contador = [0]

    def dibujar_paso(titulo, aem_actual, visitados_actual, candidatas_display, nuevo_borde=None):
        paso_contador[0] += 1

        fig, ax = plt.subplots(figsize=(13, 9))
        fig.patch.set_facecolor('#0d1b2a')
        ax.set_facecolor('#0d1b2a')
        ax.set_title(titulo, fontsize=13, fontweight='bold',
                     color='white', pad=12)

        colores = [color_nodo(n, visitados_actual) for n in G.nodes()]

        # Aristas base (gris oscuro)
        nx.draw_networkx_edges(G, pos_torres, edge_color='#3a3a5c',
                               width=1, ax=ax)

        # Aristas candidatas (amarillo punteado)
        cand_edges = [(o, d) for _, o, d in candidatas_display]
        if cand_edges:
            nx.draw_networkx_edges(G, pos_torres, edgelist=cand_edges,
                                   edge_color='#FFD166', width=1.5,
                                   style='dotted', ax=ax)

        # Aristas del AEM (verde)
        aem_edges = [(u, v) for u, v, _ in aem_actual]
        if aem_edges:
            nx.draw_networkx_edges(G, pos_torres, edgelist=aem_edges,
                                   edge_color='#2a9d8f', width=3, ax=ax)

        if nuevo_borde:
            nx.draw_networkx_edges(G, pos_torres, edgelist=[nuevo_borde],
                                   edge_color='#06ffa5', width=4,
                                   style='dashed', ax=ax)

        # Nodos
        nx.draw_networkx_nodes(G, pos_torres, node_color=colores,
                               node_size=1800, ax=ax, alpha=0.95)

        # Etiquetas de nodos
        etiquetas = {n: n.replace(' ', '\n') for n in G.nodes()}
        nx.draw_networkx_labels(G, pos_torres, labels=etiquetas,
                                font_size=7.5, font_color='white',
                                font_weight='bold', ax=ax)

        # Pesos de aristas
        edge_labels = nx.get_edge_attributes(G, 'weight')
        edge_labels_kwh = {k: f"{v}kWh" for k, v in edge_labels.items()}
        nx.draw_networkx_edge_labels(G, pos_torres, edge_labels=edge_labels_kwh,
                                     font_size=7, font_color='#FFD166', ax=ax)

        # Leyenda
        leyenda = [
            mpatches.Patch(color='#FF4500', label='Torre origen'),
            mpatches.Patch(color='#2a9d8f', label='Torre conectada'),
            mpatches.Patch(color='#adb5bd', label='Torre pendiente'),
            mpatches.Patch(color='#06ffa5', label='Nueva conexión'),
            mpatches.Patch(color='#FFD166', label='Candidatas'),
        ]
        ax.legend(handles=leyenda, loc='lower left',
                  facecolor='#1a1a2e', edgecolor='white',
                  labelcolor='white', fontsize=8)

        plt.axis('off')
        filename = os.path.join(output_dir, f"Paso_{paso_contador[0]:02d}.png")
        plt.savefig(filename, dpi=200, bbox_inches='tight')
        plt.close(fig)
        print(f"Imagen guardada: {filename}")

    # 4. Lógica del Algoritmo de Prim
    visitados = {torre_inicio}
    candidatas = []
    aem = []
    energia_total = 0

    for vecina, energia in campus_torres.get(torre_inicio, []):
        heapq.heappush(candidatas, (energia, torre_inicio, vecina))

    print(f"\n Inicio desde: {torre_inicio}")
    dibujar_paso(f"Paso 0: Inicio en '{torre_inicio}'",
                 [], visitados, candidatas)

    while candidatas and len(visitados) < len(campus_torres):
        energia, origen, destino = heapq.heappop(candidatas)

        if destino not in visitados:
            visitados.add(destino)
            aem.append((origen, destino, energia))
            energia_total += energia

            print(f"\n PASO {len(aem)}: Conectar '{origen}' ──{energia}kWh──▶ '{destino}'")
            print(f"     Energía acumulada: {energia_total} kWh")

            dibujar_paso(
                f"Paso {len(aem)}: '{origen}' → '{destino}' | {energia}kWh | Acumulado: {energia_total}kWh",
                aem, visitados, candidatas, (origen, destino)
            )

            for vecina, nuevo_energia in campus_torres.get(destino, []):
                if vecina not in visitados:
                    heapq.heappush(candidatas, (nuevo_energia, destino, vecina))

        else:
            print(f"\n DESCARTADA: '{origen}' ──{energia}kWh──▶ '{destino}'  (formaría ciclo)")
            dibujar_paso(
                f"Descartada: '{origen}'→'{destino}' (ciclo)",
                aem, visitados, candidatas
            )

    # 5. Resultado final
    print("\n" + "═" * 56)
    print("  Conexiones seleccionadas:\n")
    for u, v, e in aem:
        print(f"   {u}  ←→  {v}   |  {e} kWh")
    print(f"\n Consumo minimo total: {energia_total} kWh")
    print(f" Pasos guardados en: '{output_dir}/'\n")

    dibujar_paso(
        f"Red WiFi Óptima Final | Consumo Total: {energia_total} kWh",
        aem, visitados, []
    )


# Datos

if __name__ == "__main__":

    campus_torres = {
        'Rectoría':      [('Biblioteca', 3),  ('Aulas A', 5),   ('Cafetería', 7)],
        'Biblioteca':    [('Rectoría', 3),    ('Aulas A', 4),   ('Lab. Cómputo', 6)],
        'Aulas A':       [('Rectoría', 5),    ('Biblioteca', 4),('Aulas B', 2),    ('Lab. Ciencias', 8)],
        'Aulas B':       [('Aulas A', 2),     ('Lab. Ciencias', 5), ('Gimnasio', 9)],
        'Lab. Cómputo':  [('Biblioteca', 6),  ('Lab. Ciencias', 3), ('Dormitorios', 7)],
        'Lab. Ciencias': [('Aulas A', 8),     ('Aulas B', 5),   ('Lab. Cómputo', 3), ('Estadio', 6)],
        'Cafetería':     [('Rectoría', 7),    ('Gimnasio', 4),  ('Dormitorios', 5)],
        'Gimnasio':      [('Cafetería', 4),   ('Aulas B', 9),   ('Estadio', 3)],
        'Estadio':       [('Gimnasio', 3),    ('Lab. Ciencias', 6), ('Dormitorios', 8)],
        'Dormitorios':   [('Cafetería', 5),   ('Lab. Cómputo', 7),  ('Estadio', 8)],
    }

    # Posiciones en el mapa del campus
    pos_campus = {
        'Rectoría':      (0.0,  1.5),
        'Biblioteca':    (-1.2, 0.8),
        'Aulas A':       (0.0,  0.5),
        'Aulas B':       (1.2,  0.5),
        'Lab. Cómputo':  (-1.5,-0.5),
        'Lab. Ciencias': (1.0, -0.5),
        'Cafetería':     (-0.5,-1.5),
        'Gimnasio':      (1.5, -1.2),
        'Estadio':       (2.0,  0.0),
        'Dormitorios':   (-0.5,-2.5),
    }

    torre_inicio = 'Rectoría'
    prim_wifi_campus(campus_torres, pos_campus, torre_inicio)