import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 1. Clase Union-Find
class UnionFind:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_j] = root_i
            return True
        return False


# 2. Algoritmo para hospitales
def kruskal_hospitales(centros, rutas):
    """
    Encuentra la red de traslado de pacientes de menor costo
    que conecta todos los centros médicos.
    Cada arista representa una ruta posible entre dos centros
    y su peso es el costo de instalación en miles de pesos.
    """

    print("\n Pesos = Costo de instalación de ruta (miles de pesos)")
    print(f" Centros médicos: {', '.join(sorted(centros))}\n")

    # Ordenar rutas por costo (menor a mayor)
    rutas_ordenadas = sorted(rutas, key=lambda r: r[2])

    print(" RUTAS DISPONIBLES (ordenadas por costo):")
    print(f"  {'Origen':<22} {'Destino':<22} {'Costo'}")
    print("  " + "─" * 52)
    for u, v, w in rutas_ordenadas:
        print(f"  {u:<22} {v:<22} ${w}k")

    print("\n" + "─" * 58)
    print("Procesando todas las rutas paso a paso:\n")

    uf = UnionFind(centros)
    red_minima = []
    costo_total = 0
    paso = 1

    for u, v, w in rutas_ordenadas:
        root_u = uf.find(u)
        root_v = uf.find(v)

        print(f"  PASO {paso}: Evaluar ruta  {u}  ──$${w}k──  {v}")

        if root_u != root_v:
            uf.union(u, v)
            red_minima.append((u, v, w))
            costo_total += w
            print(f"          ACEPTADA — No forma ciclo. Costo acumulado: ${costo_total}k\n")
        else:
            print(f"          RECHAZADA — Formara un ciclo.\n")

        paso += 1

        if len(red_minima) == len(centros) - 1:
            print(" Red completa: todos los centros están conectados.")
            break

    # Resultado final
    print("\n" + "═" * 58)
    print("\n  Rutas seleccionadas para la red médica óptima:\n")
    for u, v, w in red_minima:
        print(f"    🔗 {u}  ←→  {v}   |  Costo: ${w}k")
    print(f"\n  Costo minimo total: ${costo_total}k\n")

    # Generar gráfico
    visualizar_red_medica(centros, rutas, red_minima, costo_total)


def visualizar_red_medica(centros, todas_rutas, red_minima, costo_total):
    """
    Dibuja el mapa de la red médica con estilo hospitalario.
    Verde = rutas seleccionadas (red óptima)
    Rojo  = rutas descartadas
    """
    G = nx.Graph()
    G.add_nodes_from(centros)

    edge_labels = {}
    for u, v, w in todas_rutas:
        G.add_edge(u, v, weight=w)
        edge_labels[(u, v)] = f"${w}k"

    pos = nx.spring_layout(G, seed=7, k=3.0)

    # Clasificar aristas
    red_minima_simple = [(u, v) for u, v, w in red_minima]
    descartadas = [
        (u, v) for u, v, w in todas_rutas
        if (u, v) not in red_minima_simple and (v, u) not in red_minima_simple
    ]

    # Colores de nodos por tipo
    tipo_nodo = {
        'Hospital General':     'H',
        'Hospital Regional':    'H',
        'Clínica Norte':        'C',
        'Clínica Sur':          'C',
        'Clínica Este':         'C',
        'Centro de Urgencias':  'U',
    }
    colores_nodo = []
    for nodo in G.nodes:
        t = tipo_nodo.get(nodo, 'C')
        if t == 'H':   colores_nodo.append('#E63946')   # Rojo — Hospital
        elif t == 'U': colores_nodo.append('#F4A261')   # Naranja — Urgencias
        else:          colores_nodo.append('#457B9D')   # Azul — Clínica

    # Dibujar
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_facecolor('#f0f4f8')
    fig.patch.set_facecolor('#f0f4f8')

    plt.title(
        f"Red de Centros Médicos \nCosto Mínimo de Instalación: ${costo_total}k",
        fontsize=14, fontweight='bold', color='#1d3557', pad=15
    )

    # Aristas descartadas
    nx.draw_networkx_edges(G, pos, edgelist=descartadas,
                           width=1.5, alpha=0.35, edge_color='#e63946',
                           style='dashed', ax=ax)

    # Aristas de la red mínima
    nx.draw_networkx_edges(G, pos, edgelist=red_minima_simple,
                           width=4, alpha=0.9, edge_color='#2a9d8f', ax=ax)

    # Nodos
    nx.draw_networkx_nodes(G, pos, node_color=colores_nodo,
                           node_size=2500, ax=ax, alpha=0.95)

    # Etiquetas de nodos
    etiquetas = {n: n.replace(' ', '\n') for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=etiquetas,
                            font_size=8, font_color='white',
                            font_weight='bold', ax=ax)

    # Etiquetas de costos
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=8.5, font_color='#1d3557', ax=ax)

    # Leyenda
    leyenda = [
        mpatches.Patch(color='#E63946',  label='Hospital'),
        mpatches.Patch(color='#F4A261',  label='Centro de Urgencias'),
        mpatches.Patch(color='#457B9D',  label='Clínica'),
        mpatches.Patch(color='#2a9d8f',  label='Ruta seleccionada (red óptima)'),
        mpatches.Patch(color='#e63946',  label='Ruta descartada', alpha=0.4),
    ]
    ax.legend(handles=leyenda, loc='lower left', facecolor='white',
              edgecolor='#1d3557', fontsize=9)

    plt.axis('off')
    nombre_archivo = "Red_Medica.png"
    plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   Gráfico guardado como: {nombre_archivo}")
    print("  Búscalo en la carpeta donde ejecutaste el script.\n")


# Datos

if __name__ == "__main__":

    centros_medicos = {
        'Hospital General',
        'Hospital Regional',
        'Clínica Norte',
        'Clínica Sur',
        'Clínica Este',
        'Centro de Urgencias',
    }

    # (Centro A, Centro B, Costo de instalación en miles de pesos)
    rutas_posibles = [
        ('Hospital General',    'Hospital Regional',   15),
        ('Hospital General',    'Clínica Norte',        8),
        ('Hospital General',    'Centro de Urgencias', 20),
        ('Hospital Regional',   'Clínica Este',        10),
        ('Hospital Regional',   'Clínica Sur',         13),
        ('Clínica Norte',       'Clínica Este',         6),
        ('Clínica Norte',       'Centro de Urgencias', 17),
        ('Clínica Sur',         'Centro de Urgencias',  9),
        ('Clínica Sur',         'Clínica Este',        11),
        ('Clínica Este',        'Centro de Urgencias', 14),
    ]

    kruskal_hospitales(centros_medicos, rutas_posibles)