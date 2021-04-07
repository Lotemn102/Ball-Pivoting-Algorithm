import numpy as np
import matplotlib.pyplot as plt


def render(array):
    fig = plt.figure(dpi=120)
    ax = fig.add_subplot(111, projection='3d')

    element = {
        "top": np.asarray([[[0, 1], [0, 1]], [[0, 0], [1, 1]], [[1, 1], [1, 1]]]),
        "bottom": np.asarray([[[0, 1], [0, 1]], [[0, 0], [1, 1]], [[0, 0], [0, 0]]]),
        "left": np.asarray([[[0, 0], [0, 0]], [[0, 1], [0, 1]], [[0, 0], [1, 1]]]),
        "right": np.asarray([[[1, 1], [1, 1]], [[0, 1], [0, 1]], [[0, 0], [1, 1]]]),
        "front": np.asarray([[[0, 1], [0, 1]], [[0, 0], [0, 0]], [[0, 0], [1, 1]]]),
        "back": np.asarray([[[0, 1], [0, 1]], [[1, 1], [1, 1]], [[0, 0], [1, 1]]])
    }

    for l in range(0, 10):
        for m in range(0, 10):
            for n in range(0, 10):
                recipe, l_f, m_f, n_f = ('even', 0.1, 0.1, 0.1)
                relative_pos = (l*l_f, m*m_f, n*n_f)

                for side in element:
                    (Ls, Ms, Ns) = (
                        1 * (element[side][0] + l) + relative_pos[0],
                        1 * (element[side][1] + m) + relative_pos[1],
                        1 * (element[side][2] + n) + relative_pos[2]
                    )
                    ax.plot_surface(
                        Ls, Ns, Ms,
                        rstride=1, cstride=1,
                        alpha=0.2,
                        color='red'
                    )

    ax.axis('off')
    plt.show()


subject = np.arange(0, 125).reshape((5, 5, 5))
render(array=subject)
