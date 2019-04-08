import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anime
import sympy as sp


class fonc_diff_infini:
    """
    Classe de fonction en C-diff-infini R^2->R^2
    Ici, on pense que un diffeomorphisme est un objet dans le classe de fonction en C-diff-infini R^2->R^2.
    On declare un tel objet par une expression de sympy, qui prend deux arguments x et y, et retourne deux valeurs.
    Par ex.:
        x,y=sp.symbols("x y")
        expr=(x+y,x*y)
        ex=fonc_diff_infini(expr,(x,y))
    """

    def __init__(self, expr, expr_inv=None, vars_sym=(sp.symbols("x y"))):
        self._expr = expr
        self._expr_inv = expr_inv
        self._x, self._y = vars_sym
        self._num = sp.lambdify((self._x, self._y), self._expr, "numpy")
        self._df_sym = None
        self._df_num = None
        self._plan = [None, None, None, None]  # t0, t1, taille, plan
        self._tab_f = [None, None, None, None]  # t0, t1, taille, f(plan)
        self._tab_df = [None, None, None, None]  # t0, t1, taille, tab_df
        self._tab_angles_R = [None, None, None, None]  # t0, t1, taille, tab_angles_R
        self._simulation = None

    def sym(self):
        """
        :return: l'expression en sympy du diffeomorphisme
        """
        return self._expr

    def num(self):
        """
        Rrtourner une fonction python de l'expression symbolique du diffeomorphisme
        :return:
        """
        return self._num

    def f(self, x_num, y_num):
        return self._num(x_num, y_num)

    def plan(self, t0=-1, t1=1, taille=50):
        """
        Retourner deux tableaux qui sont les 'rastérisations' (feuillages) d'un plan traitees par numpy.meshgrid.
        Attention, la structure de ces deux tableaux sont specifiques. Veuilliez-vous afficher ces deux tableaux pour
        la connaitre. C'est pour faciliter le calcul d'apres.
        :param t0:
        :param t1:
        :param taille:
        :return:
        """
        if [t0, t1, taille] == self._plan[:3]:
            if self._plan[3] is not None:
                return self._plan[3]
        else:
            self._plan[:3] = [t0, t1, taille]
        axe_x, axe_y = np.meshgrid(np.linspace(t0, t1, taille), np.linspace(t0, t1, taille))
        self._plan[3] = axe_x, axe_y
        return axe_x, axe_y

    def tab_f(self, t0=-1, t1=1, taille=50):
        if [t0, t1, taille] == self._tab_f[:3]:
            if self._tab_f[3] is not None:
                return self._tab_f[3]
        self._tab_f[:3] = [t0, t1, taille]
        axe_x, axe_y = self.plan(t0, t1, taille)
        tab_x, tab_y = self.f(axe_x, axe_y)
        self._tab_f[3] = (tab_x, tab_y)
        return tab_x, tab_y

    def df_sym(self):
        """
        对一个符号表达函数f：I^2->I^2求其微分表达式。注意返回的矩阵是一个一维列表，先从上到下，再从左到右
        Pour une fonction symbolique f：I^2->I^2, on calcul son différentiel.
        Attention, le résultat est un liste en 1 dimensionla, en lisant la matrice de différentiel de haut à bas,
        et de gauche à droit
        :param _f:
        :return: | &φ1/&x  &φ1/&y |
                  | &φ2/&x  &φ2/&y |
        """
        if self._df_sym is None:
            self._df_sym = sp.Matrix([[sp.diff(self._expr[0], self._x), sp.diff(self._expr[0], self._y)],
                                      [sp.diff(self._expr[1], self._x), sp.diff(self._expr[1], self._y)]])
        return self._df_sym

    def df_num(self):
        """
        Rrtourner une fonction python de l'expression symbolique du differentiel du diffeomorphisme
        :return:
        """
        if self._df_num is None:
            self._df_num = sp.lambdify((self._x, self._y), self.df_sym(), "numpy")
        return self._df_num

    def df(self, x_num, y_num):
        """
        C'est la version de fonction python du differentiel du diffeomorphisme, qui prend en argument x_num et y_num,
        et qui retourne le differentiel (matrice jacobienne) dans ce point.
        :param x_num:
        :param y_num:
        :return:
        """
        return self.df_num()(x_num, y_num)

    def draw(self, direction='a', t0=-1, t1=1, taille=50, display=True):
        """
        Afficher le diffeomorphisme par une image en 2D
        :param direction: soit 'h' pour la direction horientale, soit 'v' pour la direction verticale, soit l'autre pour
         tous afficher en une meme image
        :param t0:
        :param t1:
        :param taille:
        :return:
        """
        tab_x, tab_y = self.tab_f(t0, t1, taille)
        if direction == 'h':
            plt.title("Diffeomorphisme dans la direction horientale")
            plt.plot(tab_x.T, tab_y.T)
        elif direction == 'v':
            plt.title("Diffeomorphisme dans la direction verticale")
            plt.plot(tab_x, tab_y)
        else:
            plt.title("Diffeomorphisme")
            plt.plot(tab_x.T, tab_y.T)
            plt.plot(tab_x, tab_y)
        if display:
            plt.show()

    def tab_df(self, t0=-1, t1=1, taille=50):
        """
        En utilisant un plan feuillage par numpy.meshgrid, on symplifie le code pour calculer un tableau de matrice
        jacobienne de chaque point dans le plan.
        Attention, le resultat retourne est en la structure de meshgrid. Voir detailles dans la partie ":return"
        :param t0:
        :param t1:
        :param taille:
        :return: le resultat est en numpy.array. Soit [[a,b],[c,d]] la matrice jacobienne du diffeomorphisme dans
        un point, resultat[0][0] contient les a de chaque point ET DANS LA TRUCTURE DE numpy.meshgrid. De meme,
        resultat[0][1] contient les c, resultat[1][0] contient les b, et resultat[1][1] contient les d.
        """
        if [t0, t1, taille] == self._tab_df[:3]:
            if self._tab_df[3] is not None:
                return self._tab_df[3]
        else:
            self._tab_df[:3] = [t0, t1, taille]

        if self._df_num is None:
            self.df_num()

        axe_x, axe_y = self.plan(t0, t1, taille)
        self._tab_df[3] = self._df_num(axe_x, axe_y)
        return self._tab_df[3]

    def draw_df(self, direction='a', t0=-1, t1=1, taille=50, display=True):
        """
        Afficher le champ de vecteurs pour un diffeomorphisme, les autres sont parailles que draw
        :param direction:
        :param t0:
        :param t1:
        :param taille:
        :return:
        """
        tab_x, tab_y = self.tab_f(t0, t1, taille)
        tab_df = self.tab_df(t0, t1, taille)
        if direction == 'h':
            plt.quiver(tab_x, tab_y, tab_df[0][0], tab_df[1][0])
            plt.xlabel(r'$x_1$')
            plt.ylabel(r'$x_2$')
            plt.title("Champ de vecteurs horientals")
        elif direction == 'v':
            plt.quiver(tab_x, tab_y, tab_df[0][1], tab_df[1][1])
            plt.xlabel(r'$y_1$')
            plt.ylabel(r'$y_2$')
            plt.title("Champ de vecteurs verticals")
        else:
            plt.quiver(tab_x, tab_y, tab_df[0][0], tab_df[1][0])
            plt.quiver(tab_x, tab_y, tab_df[0][1], tab_df[1][1])
            plt.xlabel(r'$x_1$ et $y_1$')
            plt.ylabel(r'$x_2$ et $y_2$')
            plt.title("Champ de vecteurs")
        if display:
            plt.show()

    def draw_all(self, direction='a', t0=-1, t1=1, taille=50, display=True):
        """
        Pour un diffeomorphisme, afficher une fois lui-meme et son champ de vecteurs en une figure, les aures sont
        parailles que draw et que draw_df
        :param direction:
        :param t0:
        :param t1:
        :param taille:
        :return:
        """
        if direction == 'h':
            self.draw('h', t0, t1, taille, False)
            title = "Diffeomorphisme et son champ de vecteurs dans le sens horiental"
        elif direction == 'v':
            self.draw('v', t0, t1, taille, False)
            title = "Diffeomorphisme et son champ de vecteurs dans le sens vertical"
        else:
            self.draw('a', t0, t1, taille, False)
            title = "Diffeomorphisme et son champ de vecteurs"
        self.draw_df(direction, t0, t1, taille, False)
        plt.title(title)
        if display:
            plt.show()

    def tab_angles_R(self, t0=-1, t1=1, taille=50):
        if [t0, t1, taille] == self._tab_angles_R[:3]:
            if self._tab_angles_R[3] is not None:
                return self._tab_angles_R[3]
        else:
            self._tab_angles_R[:3] = [t0, t1, taille]

        tab_df = self.tab_df(t0, t1, taille)
        tab_angles_x_2pi = np.arctan2(tab_df[1][0], tab_df[0][0])
        tab_angles_y_2pi = np.arctan2(tab_df[1][1], tab_df[0][1])

        def modulo_2pi(x):
            y = x
            while y > math.pi:
                y -= 2 * math.pi
            while y < -math.pi:
                y += 2 * math.pi
            return y

        def corrigeur(tab):
            tab_R = []
            for ligne in tab:
                ligne_R = [ligne[0]]
                for angle in ligne[1:]:
                    prec = ligne_R[-1]
                    ligne_R.append(prec + modulo_2pi(angle - prec))
                tab_R.append(ligne_R)
            return np.array(tab_R)

        tab_angles_x_R = corrigeur(tab_angles_x_2pi)
        tab_angles_y_R = corrigeur(tab_angles_y_2pi.T) - math.pi / 2

        # self._tab_angles_R[3] = np.array(tab_angles_x_R), np.array(tab_angles_y_R)
        self._tab_angles_R[3] = np.array([tab_angles_x_R, tab_angles_y_R])
        return self._tab_angles_R[3]

    def draw_angles_ligne(self, direction, t0=-1, t1=1, taille=50, indice=None, val_min=None, val_max=None,
                          display=True):
        if direction == 'h':
            case = 0
            direction_str = "ligne"
        else:
            case = 1
            direction_str = "colonne"
        ind = indice
        if ind is None:
            ind = taille // 2
        v_min, v_max = val_min, val_max
        tick = 0.25 * math.pi
        tab = ex.tab_angles_R(t0, t1, taille)[case][ind]
        if v_min is None:
            v_min = (min(tab) // tick - 1) * tick
        if v_max is None:
            v_max = (max(tab) // tick + 2) * tick
        axe = np.linspace(t0, t1, taille)
        plt.title("Angles de la ${}-ieme$ {} sur {} en total".format(ind, direction_str, taille))
        my_y_ticks = np.arange(v_min, v_max, tick)
        plt.yticks(my_y_ticks)
        plt.xlabel("x")
        plt.ylabel('$\Theta$')
        res = plt.plot(axe, tab)
        if display:
            plt.show()
        return res

    def play_angles(self, direction, t0=-1, t1=1, taille=50, bsave=True, save_name=None):
        fig = plt.figure()
        if direction == 'h':
            case = 0
        else:
            case = 1
        tab = np.array(self.tab_angles_R(t0, t1, taille)[case])
        tick = 0.25 * math.pi
        val_min = (tab.min() // tick - 1) * tick
        val_max = (tab.max() // tick + 2) * tick
        tab_fig = []
        for i in range(taille):
            tab_fig.append(self.draw_angles_ligne(direction, t0, t1, taille, i, val_min, val_max, False))
        im_ani = anime.ArtistAnimation(fig, tab_fig, interval=50, repeat_delay=3000, blit=True)
        if bsave:
            name = save_name
            if name is None:
                name = "animation"
            im_ani.save(name + ".html")
        return im_ani

    def _distance(self, x_, y_, tab_x_mesh, tab_y_mesh):
        """
        Pour chaque point dans l'ensemble donne (tab_x_mesh, tab_y_mesh), calculer la distance euclidienne entre lui et
        le point (x_,y_)
        :param x_:
        :param y_:
        :param tab_x_mesh:
        :param tab_y_mesh:
        :return:
        """
        tempx = tab_x_mesh - x_
        tempy = tab_y_mesh - y_
        tab_2d = []
        for i in range(len(tab_x_mesh)):
            tab_2d.append(np.sqrt(tempx[i] ** 2 + tempy[i] ** 2))
        return np.array(tab_2d)

    def _classifier_tab(self, tab_dis, tab_x_mesh, tab_y_mesh, pas, n):
        """
        Classier les points dans l'ensemble donne (tab_x_mesh, tab_y_mesh), par leur distance:
        [0, pas/2) [pas/2, pas + pas/2) [pas + pas/2, 2*pas + pas/2) ... [(n-2)*pas + pas/2, (n-1)*pas + pas/2)
        (>=(n-1)*pas + pas/2)
        :param tab_dis: les distances des points dans (tab_x_mesh, tab_y_mesh):
         tab_2d[i,j]->tab_x_mesh[i,j],tab_y_mesh[i,j]
        :param tab_x_mesh:
        :param tab_y_mesh:
        :param pas: la distance entre deux points adjacents dans une meme ligne de la grille du plan [t0, t1]^2
        :param n: le nombre des niveaux de classification
        :return:
        """
        tab_res_x = [[] for i in range(n + 1)]
        tab_res_y = [[] for i in range(n + 1)]
        tab_dis_bis = (tab_dis - pas / 2) // pas + 1
        for i in range(len(tab_dis_bis)):
            for j in range(len(tab_dis_bis[i])):
                niveau = int(tab_dis_bis[i, j])
                if niveau >= n:
                    tab_res_x[n].append(tab_x_mesh[i, j])
                    tab_res_y[n].append(tab_y_mesh[i, j])
                else:
                    tab_res_x[niveau].append(tab_x_mesh[i, j])
                    tab_res_y[niveau].append(tab_y_mesh[i, j])
        return tab_res_x, tab_res_y

    def _classifier_points_cles(self, tab_dis, tab_x_mesh, tab_y_mesh, pas, n):
        tab_res_x = [[] for i in range(n + 1)]
        tab_res_y = [[] for i in range(n + 1)]
        tab_dis_bis = tab_dis // pas + 1
        for i in range(len(tab_dis_bis)):
            for j in range(len(tab_dis_bis[i])):
                niveau = int(tab_dis_bis[i, j])
                if tab_dis[i, j] >= pas / 2 + niveau * pas:
                    niveau += 1
                elif tab_dis[i, j] <= pas / 2 + (niveau - 1) * pas:
                    niveau -= 1
                if niveau >= n:
                    tab_res_x[n].append(tab_x_mesh[i, j])
                    tab_res_y[n].append(tab_y_mesh[i, j])
                else:
                    tab_res_x[niveau].append(tab_x_mesh[i, j])
                    tab_res_y[niveau].append(tab_y_mesh[i, j])
        return tab_res_x, tab_res_y

    def tab_inverse(self, t0=-1, t1=1, taille=50, multi=10):
        axe = np.linspace(t0, t1, taille)
        axe_x, axe_y = np.meshgrid(axe, axe)
        axe2 = np.linspace(t0, t1, taille * multi)
        axe2_x, axe2_y = np.meshgrid(axe2, axe2)
        f = self._num
        ens_arrive_x, ens_arrive_y = f(axe2_x, axe2_y)

        pas = (t1 - t0) / (taille - 1)
        n = math.ceil((taille // 2) * math.sqrt(2))

        def ajustement(x_, y_, tab_x_mesh, tab_y_mesh):
            dis = np.inf
            test = (pas ** 2) / 4
            val_x, val_y = None, None
            tab_x_new, tab_y_new = [], []
            for i in range(len(tab_x_mesh)):
                tempx, tempy = [], []
                for j in range(len(tab_x_mesh[i])):
                    x_ori, y_ori = tab_x_mesh[i, j], tab_y_mesh[i, j]
                    fx, fy = f(x_ori, y_ori)
                    d = (fx - x_) ** 2 + (fy - y_) ** 2
                    if d < dis:
                        dis = d
                        val_x = x_ori
                        val_y = y_ori
                    if d >= test:
                        tempx.append(x_ori)
                        tempy.append(y_ori)
                tab_x_new.append(tempx)
                tab_y_new.append(tempy)
            return val_x, val_y, tab_x_new, tab_y_new

        tab_dis_cles = ex._distance(-1, -1, axe_x, axe_y)
        class_x, class_y = ex._classifier_points_cles(tab_dis_cles, axe_x, axe_y, pas, n)
        tab_dis = ex._distance(-1, -1, ens_arrive_x, ens_arrive_y)
        tab_inv_x, tab_inv_y = ex._classifier_tab(tab_dis, axe2_x, axe2_y, pas, n)
        for niveau in range(len(class_x)):
            for i in range(len(class_x[niveau])):

        pass

        """
        ens_depart = [(x_, y_) for x_ in np.linspace(t0, t1, taille2) for y_ in np.linspace(t0, t1, taille2)]
        ens_arrive = [self._num(p[0], p[1]) for p in ens_depart]
        ens_critere = [[(x_, y_) for x_ in np.linspace(t0, t1, taille)] for y_ in np.linspace(t0, t1, taille)]
        ens_inverse = []
        for ligne in ens_critere:
            ligne_inverse = []
            for pc in ligne:
                dif_min = np.inf
                point_proche = None
                for i in range(taille2 ** 2):
                    dif = (ens_arrive[i][0] - pc[0]) ** 2 + (ens_arrive[i][1] - pc[1]) ** 2
                    if dif < dif_min:
                        dif_min = dif
                        point_proche = ens_depart[i]
                ligne_inverse.append(point_proche)
            ens_inverse.append(ligne_inverse)
        return ens_inverse
        """

    def _find_sim_points(self, x_, y_, t0=-1, t1=1, taille=50):
        pas = (t1 - t0) / (taille - 1)
        kx0 = int((x_ - t0) // pas)
        if kx0 >= taille:
            kx0 = taille - 1
        kx1 = kx0 + 1 if kx0 < taille - 1 else kx0
        t = (x_ - t0 - kx0 * pas) / pas
        ky0 = int((y_ - t0) // pas)
        if ky0 >= taille:
            ky0 = taille - 1
        ky1 = ky0 + 1 if ky0 < taille - 1 else ky0
        s = (y_ - t0 - ky0 * pas) / pas
        return (kx0, ky0), (kx1, ky0), (kx0, ky1), (kx1, ky1), t, s

    def _angle_moyen(self, tab_angles, p00, p10, p01, p11, t, s):
        a00 = np.array([tab_angles[0, p00[0], p00[1]], tab_angles[1, p00[1], p00[0]]])
        a10 = np.array([tab_angles[0, p10[0], p10[1]], tab_angles[1, p10[1], p10[0]]])
        a01 = np.array([tab_angles[0, p01[0], p01[1]], tab_angles[1, p01[1], p01[0]]])
        a11 = np.array([tab_angles[0, p11[0], p11[1]], tab_angles[1, p11[1], p11[0]]])
        angle = (1 - t) * ((1 - s) * a00 + s * a01) + t * ((1 - s) * a10 + s * a11)
        return angle

    def trace(self, tab_angles, t0=-1, t1=1, taille=50, precision=0.01):
        axe = np.linspace(t0, t1, taille)
        tab_h = []
        plt.figure(figsize=(30, 30))
        for y_ in axe:
            tab_trace_hx, tab_trace_hy = [-1.0], [y_]
            while tab_trace_hx[-1] < t1:
                p00, p10, p01, p11, t, s = self._find_sim_points(tab_trace_hx[-1], tab_trace_hy[-1], t0, t1, taille)
                # print("point: {}, avec ".format((tab_trace_x[-1], tab_trace_y[-1])), p00, p10, p01, p11, t, s)
                angle_moy = self._angle_moyen(tab_angles, p00, p10, p01, p11, t, s)
                tab_trace_hx.append(tab_trace_hx[-1] + precision * math.cos(angle_moy[0]))
                tab_trace_hy.append(tab_trace_hy[-1] + precision * math.sin(angle_moy[1]))
            tab_h.append([tab_trace_hx, tab_trace_hy])
            plt.plot(tab_trace_hx, tab_trace_hy)
        plt.show()
        """
        plt.figure(figsize=(30, 30))
        for x_ in axe:
            tab_trace_vx, tab_trace_vy = [x_], [-1.0]
            while tab_trace_vx[-1] < t1:
                p00, p10, p01, p11, t, s = self._find_sim_points(tab_trace_vx[-1], tab_trace_vy[-1], t0, t1, taille)
                # print("point: {}, avec ".format((tab_trace_x[-1], tab_trace_y[-1])), p00, p10, p01, p11, t, s)
                angle_moy = self._angle_moyen(tab_angles, p00, p10, p01, p11, t, s)
                tab_trace_vx.append(tab_trace_vx[-1] + precision * math.cos(angle_moy[1]))
                tab_trace_vy.append(tab_trace_vy[-1] + precision * math.sin(angle_moy[1]))
            tab_h.append([tab_trace_vx, tab_trace_vy])
            plt.plot(tab_trace_vx, tab_trace_vy)
        plt.show()
        """
        return tab_h


def f_ex(a, b, x_sym=sp.Symbol('x'), y_sym=sp.Symbol('y')):
    """
    返回同一个函数的两个形式，第一个用sympy符号表达，第二个用python函数表达
    Retouner deux formes d'une même fonction mathematique. La première est exprimée par des symboles de sympy,
    la deuxième est exprimée par une fonction de python.
    :param a:
    :param b:
    :param x_sym:
    :param y_sym:
    :return:
    """

    def f_num(x_num, y_num):
        return x_num, y_num + a * np.exp(-b * y_num ** 2 - b * x_num ** 2)

    return (x_sym, y_sym + a * sp.exp(-b * y_sym ** 2 - b * x_sym ** 2)), f_num


def g_ex2(a, b, x_sym=sp.Symbol('x'), y_sym=sp.Symbol('y')):
    g_sym = a * sp.exp(-b * (x_sym ** 2 + y_sym ** 2))

    def g_num(x_num, y_num):
        return a * np.exp(-b * (x_num ** 2 + y_num ** 2))

    return g_sym, g_num


def r_ex2(_theta, g_sym, g_num, x_sym=sp.Symbol('x'), y_sym=sp.Symbol('y')):
    f_new_sym = (sp.cos(_theta * g_sym) * x_sym - sp.sin(_theta * g_sym) * y_sym,
                 sp.sin(_theta * g_sym) * x_sym + sp.cos(_theta * g_sym) * y_sym)

    def f_new_num(x_num, y_num):
        temps = g_num(x_num, y_num)
        return np.cos(_theta * temps) * x_num - np.sin(_theta * temps) * y_num, np.sin(_theta * temps) * x_num + np.cos(
            _theta * temps) * y_num

    return f_new_sym, f_new_num


def f_ex2(a, b, _theta, x_sym=sp.Symbol('x'), y_sym=sp.Symbol('y')):
    g_sym, g_num = g_ex2(a, b, x_sym, y_sym)
    return r_ex2(_theta, g_sym, g_num, x_sym, y_sym)


""" Zone de tester le code"""
x, y = sp.symbols("x y")
le_t0, le_t1, la_taille = -1, 1, 200
expr = f_ex2(0.2, 5, 5 * math.pi)[0]
# expr = x + 0.2 * sp.exp(-15 * (x ** 2 + y ** 2)), y + 0.045 * sp.exp(-10 * (x ** 2 + y ** 2))
ex = fonc_diff_infini(expr)
# print(ex.sym())
# print(ex.num())
# print(ex.f(0, 0))
# print(ex.df_sym())
# print(ex.df(0, 0))
# ex.draw()
# ex.draw('h')
# ex.draw('v')
# print(ex.tab_df())
# ex.draw_df()
# ex.draw_df('h')
# ex.draw_df('v')
# ex.draw_all()
# ex.draw_all('h')
# ex.draw_all('v')
# print(ex.tab_df(le_t0, le_t0, la_taille))
# print(ex.tab_angles_R(-le_t0, le_t1, la_taille))
# ex.draw_angles_ligne('h', taille=la_taille, indice=la_taille // 4, val_min=-0.01, val_max=0.01)
# ex.draw_angles_ligne('v', taille=la_taille, indice=la_taille // 4, val_min=-0.01, val_max=0.01)
# ani = ex.play_angles('h',bsave=False)
# tr = ex.trace(ex.tab_angles_R(le_t0, le_t1, la_taille), le_t0, le_t1, la_taille, 0.0001)
axe = np.linspace(-1, 1, 20)
xx, yy = np.meshgrid(axe, axe)
tab_distance = ex._distance(-1, -1, xx, yy)
nn = math.ceil((20 // 2) * math.sqrt(2))
resx, resy = ex._classifier_points_cles(tab_distance, xx, yy, 2 / 19, nn)
for i in range(len(resx)):
    plt.scatter(resx[i], resy[i])
    plt.show()
