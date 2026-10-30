# Обрыв цепочки Фоккера–Планка для уравнения с запаздыванием и метод Канторовича

## Обозначения

| знак | смысл |
|---|---|
| $x(t)$ | случайная траектория |
| $W(t)$, $dW$ | винеровский процесс и его приращение за $dt$ |
| $P(x,t)$ | плотность распределения $x(t)$ |
| $P_n(x_n,t_n;\dots;x_1,t_1)$ | совместная плотность в $n$ моментов, $t_n\ge\dots\ge t_1$ |
| $\mathbb E$ | среднее по траекториям |
| $f(x)$ | пробная функция (любая гладкая) |
| $F_m$ | свёрнутые функции: $F_0=P$, $F_1=V$, $F_2=Z$, $F_3=Y$ |
| $w,\Theta,\Lambda$ | средние произведений $\varphi$ в 2, 3, 4 моментах |
| $\langle a,b\rangle$ | интеграл произведения по указанным переменным |

---

## 1. Модель

$$
\dot x(t)=-\gamma\,\varphi\bigl(x(t-\tau)\bigr)+\sqrt{2D}\,\xi(t),\qquad x(0)=0,\qquad x(t)=0\ \text{при}\ t<0,\qquad\varphi(0)=0,
$$
где $\xi(t)$ — белый шум: $\mathbb E\,\xi(t)=0$, $\mathbb E\,\xi(t)\xi(t')=\delta(t-t')$. В дифференциалах, с $W(t)=\int_0^t\xi\,dt'$:
$$
dx(t)=-\gamma\,\varphi\bigl(x(t-\tau)\bigr)\,dt+\sqrt{2D}\,dW(t).
$$

---

## 2. Шум

Разобьём $[0,t]$ на $N=t/dt$ отрезков, $W(t)=\sum_{k=1}^N dW_k$. Приращения на разных отрезках независимы и одинаково распределены, поэтому
$$
\operatorname{Var}W(t+u)=\operatorname{Var}W(t)+\operatorname{Var}W(u)\ \Rightarrow\ \operatorname{Var}W(t)=c\,t,
$$
а нормировка белого шума даёт $c=1$:
$$
\operatorname{Var}W(t)=\int_0^t\!\!\int_0^t\delta(t'-t'')\,dt'\,dt''=t .
$$
Отсюда и из $\mathbb E\,\xi=0$:
$$
\mathbb E\,dW=0,\qquad \operatorname{Var}W(t)=N\operatorname{Var}dW=t\ \Rightarrow\ \mathbb E\,(dW)^2=dt,\qquad dW\sim\sqrt{dt}.
$$
$dW(t)$ не зависит от траектории до момента $t$.

---

## 3. Плотности и пробные функции

$$
\mathbb E\,f\bigl(x(t)\bigr)=\int f(x)\,P(x,t)\,dx,\qquad
\mathbb E\,g\bigl(x(t_n),\dots,x(t_1)\bigr)=\int\!\cdots\!\int g\,P_n(x_n,t_n;\dots;x_1,t_1)\,dx_n\cdots dx_1 .
$$

Пробные функции $f$ берём гладкими и финитными (равными нулю вне конечного отрезка).

**Лемма.** Если $\int f(x)\,A(x)\,dx=0$ для любой такой $f$, то $A(x)\equiv0$. (Достаточно взять $f$ — узкий горбик вокруг произвольной точки.)

**Интегрирование по частям.** Для финитной $f$ граничные члены равны нулю:
$$
\int f'\,v\,dx=-\int f\,v'\,dx .
$$

---

## 4. Формула Ито

Разложение Тейлора при сдвиге $dx=a\,dt+b\,dW$, где $a=-\gamma\varphi(x(t-\tau))$, $b=\sqrt{2D}$:
$$
f(x+dx)-f(x)=f'(x)\,dx+\tfrac12f''(x)\,(dx)^2+O\bigl((dx)^3\bigr).
$$
Порядки:
$$
(dx)^2=\underbrace{a^2dt^2}_{dt^2}+\underbrace{2ab\,dt\,dW}_{dt^{3/2}}+\underbrace{b^2(dW)^2}_{dt},\qquad(dx)^3\sim dt^{3/2}.
$$
С точностью до членов порядка выше $dt$, $(dx)^2=2D\,dt$. Замена $(dW)^2\to dt$ понимается в среднем: $\mathbb E\,(dW)^2=dt$, а сумма $\sum_k(dW_k)^2$ по $N=t/dt$ шагам имеет среднее $t$ и дисперсию $2t\,dt\to0$. Формула (4.1) далее используется только под знаком $\mathbb E$. В $f'\,dx$ член $b f'\,dW\sim\sqrt{dt}$ сохраняется. Итог:
$$
df\bigl(x(t)\bigr)=\Bigl[-\gamma\,\varphi\bigl(x(t-\tau)\bigr)\,f'\bigl(x(t)\bigr)+D\,f''\bigl(x(t)\bigr)\Bigr]dt+\sqrt{2D}\,f'\bigl(x(t)\bigr)\,dW(t). \tag{4.1}
$$

---

## 5. Уравнение для $P$

**Усреднение.** Возьмём $\mathbb E$ от (4.1). Так как $dW(t)$ не зависит от $x(t)$,
$$
\mathbb E\bigl[f'(x(t))\,dW(t)\bigr]=\mathbb E f'(x(t))\cdot\mathbb E\,dW(t)=0 .
$$
Делим на $dt$ и переходим к пределу. Функция $F(t)=\mathbb E f(x(t))$ детерминирована, и слева стоит её производная:
$$
\frac{d}{dt}\,\mathbb E f\bigl(x(t)\bigr)=-\gamma\,\mathbb E\Bigl[\varphi\bigl(x(t-\tau)\bigr)f'\bigl(x(t)\bigr)\Bigr]+D\,\mathbb E f''\bigl(x(t)\bigr). \tag{5.1}
$$

**Переход к плотностям.**
$$
\int f\,\partial_tP\,dx=-\gamma\iint\varphi(y)\,f'(x)\,P_2(x,t;\,y,t-\tau)\,dx\,dy+D\int f''\,P\,dx .
$$

**Интегрирование по частям** (один раз в первом члене, два раза во втором) и лемма раздела 3 дают
$$
\boxed{\ \partial_tP(x,t)=D\,\partial_x^2P(x,t)+\gamma\,\partial_x\!\int\varphi(y)\,P_2(x,t;\,y,t-\tau)\,dy\ } \tag{5.2}
$$

**Отрезок $0\le t\le\tau$.** Здесь $x(t-\tau)=0$ и $\varphi(0)=0$, член с $P_2$ равен нулю, $P(x,0)=\delta(x)$:
$$
P(x,t)=P_{ex}(x,t)=\frac{1}{\sqrt{4\pi Dt}}\,e^{-x^2/(4Dt)},\qquad 0\le t\le\tau . \tag{5.3}
$$

---

## 6. Цепочка уравнений

### 6.1. Свёрнутые функции

Ранние точки входят в уравнения только через $\varphi$, поэтому интегрируем по ним с весом $\varphi$. Пусть $t_1,\dots,t_m$ — ранние моменты, $u\ge\max_jt_j$ — момент поздней точки,
$$
\Phi_m=\varphi\bigl(x(t_m)\bigr)\cdots\varphi\bigl(x(t_1)\bigr),\qquad\Phi_0=1 .
$$
Функция $F_m$ определяется равенством
$$
\int f(x)\,F_m(x,u;\,t_m,\dots,t_1)\,dx=\mathbb E\bigl[f(x(u))\,\Phi_m\bigr]\quad\text{для любой }f, \tag{6.1}
$$
то есть
$$
F_m(x,u;\,t_m,\dots,t_1)=\int\!\cdots\!\int\varphi(y_m)\cdots\varphi(y_1)\,P_{m+1}(x,u;\,y_m,t_m;\dots;y_1,t_1)\,dy_m\cdots dy_1 .
$$
$F_m$ симметрична по ранним моментам, поэтому их порядок в записи не важен. Здесь $u$ — абсолютное время поздней точки. Далее, когда ранние моменты упорядочены, $t_m\ge\dots\ge t_1$, будем также писать функции через **возраст** $a=u-t_m\ge0$:
$$
\begin{aligned}
P(x,t)&=F_0(x,t),\\
V(x,s;t_1)&=F_1(x,t_1+s;\,t_1)=\int\varphi(y)\,P_2(x,t_1+s;\,y,t_1)\,dy,\\
Z(x,r;t_2,t_1)&=F_2(x,t_2+r;\,t_2,t_1)=\iint\varphi(z)\varphi(y)\,P_3(x,t_2+r;\,z,t_2;\,y,t_1)\,dz\,dy,\\
Y(x,q;t_3,t_2,t_1)&=F_3(x,t_3+q;\,t_3,t_2,t_1)=\iiint\varphi(v)\varphi(z)\varphi(y)\,P_4(x,t_3+q;\,v,t_3;\,z,t_2;\,y,t_1)\,dv\,dz\,dy .
\end{aligned}
$$
В этих обозначениях (5.2) имеет вид
$$
\partial_tP(x,t)=D\,\partial_x^2P(x,t)+\gamma\,\partial_xV(x,\tau;\,t-\tau).
$$

### 6.2. Теорема

Для всех $m\ge0$ и $u>\max_jt_j$
$$
\partial_uF_m(x,u;\,t_m,\dots,t_1)=D\,\partial_x^2F_m(x,u;\,t_m,\dots,t_1)+\gamma\,\partial_xF_{m+1}\bigl(x,u;\,t_m,\dots,t_1,\ u-\tau\bigr), \tag{6.2}
$$
а при совпадении поздней точки с последней ранней ($u=t_m\ge t_{m-1}\ge\dots\ge t_1$, $m\ge1$)
$$
F_m(x,t_m;\,t_m,\dots,t_1)=\varphi(x)\,F_{m-1}\bigl(x,t_m;\,t_{m-1},\dots,t_1\bigr), \tag{6.3}
$$
где для $m=1$ правая часть равна $\varphi(x)\,P(x,t_1)$.

В (6.2) у функции $F_{m+1}$ добавлен ранний момент $u-\tau$. Если $u-\tau>t_m$, он становится самым поздним из ранних, и возраст $F_{m+1}$ равен $\tau$; если $u-\tau\le t_m$, возраст равен $u-t_m$. Так, при $m=0$ (6.2) — это $\partial_tP=D\,\partial_x^2P+\gamma\,\partial_xF_1(x,t;\,t-\tau)=\dots+\gamma\,\partial_xV(x,\tau;\,t-\tau)$, то есть (5.2).

### 6.3. Доказательство

Для каждого $m$ вывод один и тот же; используется только то, что $\Phi_m$ зависит от траектории до момента $u$ (все $t_j\le u$).

*Уравнение (6.2).* Запишем (4.1) для $x(u)$ на отрезке $[u,u+du]$ и умножим на $\Phi_m$; этот множитель на отрезке постоянен. Усредним. $dW(u)$ не зависит от траектории до $u$, поэтому $\mathbb E\bigl[\Phi_mf'(x(u))\,dW(u)\bigr]=0$, и
$$
\frac{d}{du}\,\mathbb E\bigl[f(x(u))\,\Phi_m\bigr]=-\gamma\,\mathbb E\bigl[f'(x(u))\,\varphi(x(u-\tau))\,\Phi_m\bigr]+D\,\mathbb E\bigl[f''(x(u))\,\Phi_m\bigr].
$$
По (6.1) левая часть равна $\int f\,\partial_uF_m\,dx$, второй член справа — $D\int f''F_m\,dx$. Вес $\varphi(x(u-\tau))\,\Phi_m$ — произведение $m+1$ множителей $\varphi$ в моменты $t_m,\dots,t_1,u-\tau$, все не позже $u$; по (6.1) первый член справа равен $-\gamma\int f'(x)\,F_{m+1}(x,u;\,t_m,\dots,t_1,u-\tau)\,dx$. Интегрирование по частям и лемма дают (6.2). При $m=0$ это в точности вывод раздела 5.

*Условие (6.3).* При $u=t_m$ выполняется $x(u)=x(t_m)$, и
$$
\mathbb E\bigl[f(x(t_m))\,\Phi_m\bigr]=\mathbb E\bigl[f(x(t_m))\,\varphi(x(t_m))\,\Phi_{m-1}\bigr]=\int f\,\varphi\,F_{m-1}\bigl(x,t_m;\,t_{m-1},\dots,t_1\bigr)\,dx .
$$
По лемме получаем (6.3). $\blacksquare$

### 6.4. Первые уравнения цепочки в переменных возраста

В уравнении для $P$ нужна $V$ возраста $\tau$. В уравнении для $V(x,s;t_1)$, $0\le s\le\tau$, добавленный момент $t_1+s-\tau\le t_1$, поэтому возраст $Z$ равен $s$; далее так же. Все функции, которые встречаются в цепочке, удовлетворяют $u-t_1\le\tau$: добавленный момент $u-\tau$ всегда самый ранний.
$$
\begin{aligned}
&\partial_tP(x,t)=D\,\partial_x^2P(x,t)+\gamma\,\partial_xV(x,\tau;\,t-\tau),\\
&\partial_sV(x,s;t_1)=D\,\partial_x^2V(x,s;t_1)+\gamma\,\partial_xZ(x,s;\,t_1,\,t_1+s-\tau),&&V(x,0;t_1)=\varphi(x)\,P(x,t_1),\\
&\partial_rZ(x,r;t_2,t_1)=D\,\partial_x^2Z(x,r;t_2,t_1)+\gamma\,\partial_xY(x,r;\,t_2,t_1,\,t_2+r-\tau),&&Z(x,0;t_2,t_1)=\varphi(x)\,V(x,t_2-t_1;\,t_1),\\
&\partial_qY(x,q;t_3,t_2,t_1)=D\,\partial_x^2Y+\gamma\,\partial_xF_4(x,t_3+q;\,t_3,t_2,t_1,\,t_3+q-\tau),&&Y(x,0;t_3,t_2,t_1)=\varphi(x)\,Z(x,t_3-t_2;\,t_2,t_1).
\end{aligned}
$$
Если хотя бы один из моментов отрицателен, $F_m=0$, так как $\varphi(x(t))=\varphi(0)=0$ при $t\le0$.

---

## 7. Обрыв

### 7.1. Где цепочка обрывается

Уравнение (6.2) для $F_m$ содержит $F_{m+1}$. На уровне $L$ мы оставляем точными уравнения для $F_0,\dots,F_{L-2}$, а функцию $F_{L-1}$, которая стоит в источнике последнего из них, заменяем приближением. По (6.2) при $m=L-2$ она берётся в аргументах
$$
F_{L-1}\bigl(x,u;\ t_{L-2},\dots,t_1,\ u-\tau\bigr),\qquad u=t_{L-2}+a .
$$
По определению (6.1) это интеграл от плотности $P_L$ с одной поздней точкой $x$ в момент $u$ и $L-1$ ранними точками:
$$
F_{L-1}\bigl(x,u;\ t_{L-2},\dots,t_1,\ u-\tau\bigr)=\int\!\cdots\!\int\varphi(y_{L-2})\cdots\varphi(y_1)\,\varphi(y_0)\;P_L\bigl(x,u;\ y_{L-2},t_{L-2};\ \dots;\ y_1,t_1;\ y_0,u-\tau\bigr)\,dy_{L-2}\cdots dy_1\,dy_0 . \tag{7.1}
$$

### 7.2. Гипотеза обрыва

Поздняя точка считается независимой от всех ранних:
$$
P_L\bigl(x,u;\ y_{L-2},t_{L-2};\ \dots;\ y_1,t_1;\ y_0,u-\tau\bigr)\ \approx\ P(x,u)\cdot P_{L-1}\bigl(y_{L-2},t_{L-2};\ \dots;\ y_1,t_1;\ y_0,u-\tau\bigr). \tag{7.2}
$$
Слева — совместная плотность $L$ точек. Справа — плотность одной поздней точки, умноженная на совместную плотность $L-1$ ранних точек. Ранние точки между собой по-прежнему связаны: их совместная плотность $P_{L-1}$ не раскладывается.

### 7.3. Что получается после подстановки

Подставим (7.2) в (7.1). Множитель $P(x,u)$ не зависит от переменных интегрирования $y_0,\dots,y_{L-2}$ и выносится за все интегралы:
$$
F_{L-1}\bigl(x,u;\ t_{L-2},\dots,t_1,\ u-\tau\bigr)\ \approx\ P(x,u)\cdot\underbrace{\int\!\cdots\!\int\varphi(y_{L-2})\cdots\varphi(y_0)\;P_{L-1}\bigl(y_{L-2},t_{L-2};\dots;y_1,t_1;\ y_0,u-\tau\bigr)\,dy_{L-2}\cdots dy_0}_{\text{число, не зависит от }x} .
$$
Оставшийся интеграл — это среднее произведения $\varphi$ по $L-1$ точкам (формула среднего через $P_{L-1}$ из раздела 3):
$$
\int\!\cdots\!\int\varphi(y_{L-2})\cdots\varphi(y_0)\,P_{L-1}\,dy_{L-2}\cdots dy_0=\mathbb E\Bigl[\varphi\bigl(x(t_{L-2})\bigr)\cdots\varphi\bigl(x(t_1)\bigr)\,\varphi\bigl(x(u-\tau)\bigr)\Bigr].
$$
Обозначим для произвольных моментов $b_1\ge b_2\ge\dots\ge b_{L-1}$
$$
M_{L-1}(b_1,\dots,b_{L-1})=\mathbb E\Bigl[\varphi\bigl(x(b_1)\bigr)\cdots\varphi\bigl(x(b_{L-1})\bigr)\Bigr]. \tag{7.3}
$$
Тогда результат обрыва:
$$
\boxed{\ F_{L-1}\bigl(x,u;\ t_{L-2},\dots,t_1,\ u-\tau\bigr)\ \approx\ M_{L-1}\bigl(t_{L-2},\dots,t_1,\ u-\tau\bigr)\;P(x,u)\ } \tag{7.4}
$$
Порядок аргументов в $M_{L-1}$ согласован с $b_1\ge\dots\ge b_{L-1}$: $t_{L-2}\ge\dots\ge t_1\ge u-\tau$, последнее — потому что для функций цепочки $u-t_1\le\tau$ (раздел 6.4).

### 7.4. Момент $M_{L-1}$ выражается через $F_{L-2}$

$M_{L-1}$ — новая величина, и систему нужно замкнуть: выразить её через функции, которые уже есть. Возьмём определение (6.1) для $F_{L-2}$ с поздней точкой в момент $b_1$ и ранними $b_2,\dots,b_{L-1}$, а в качестве пробной функции — саму $\varphi$:
$$
\int\varphi(x)\,F_{L-2}\bigl(x,b_1;\ b_2,\dots,b_{L-1}\bigr)\,dx=\mathbb E\Bigl[\varphi\bigl(x(b_1)\bigr)\,\varphi\bigl(x(b_2)\bigr)\cdots\varphi\bigl(x(b_{L-1})\bigr)\Bigr]=M_{L-1}(b_1,\dots,b_{L-1}). \tag{7.5}
$$
Здесь $\varphi$ ограничена, поэтому её можно брать как пробную функцию. Это равенство точное: в нём нет обрыва, только определение $F_{L-2}$. В переменных возраста $F_{L-2}(x,b_1;\,b_2,\dots)$ — функция возраста $b_1-b_2$.

Итак, последнее уравнение системы замыкается: его источник равен $\gamma\,M_{L-1}\,\partial_xP$, а $M_{L-1}$ вычисляется по (7.5) из $F_{L-2}$ — функции, для которой это же уравнение и написано. Все моменты в (7.5) не позже текущего $u$, поэтому $M_{L-1}$ к нужному времени уже известен.

### 7.5. Уровень 3 подробно

$L=3$, последняя точная функция — $V=F_1$, обрываем $Z=F_2$. В уравнении для $V(x,s;t_1)$ она стоит с аргументами $u=t_1+s$:
$$
Z\bigl(x,s;\ t_1,\ t_1+s-\tau\bigr)=\iint\varphi(z)\,\varphi(y)\,P_3\bigl(x,t_1+s;\ z,t_1;\ y,t_1+s-\tau\bigr)\,dz\,dy .
$$
Гипотеза (7.2):
$$
P_3\bigl(x,t_1+s;\ z,t_1;\ y,t_1+s-\tau\bigr)\approx P(x,t_1+s)\cdot P_2\bigl(z,t_1;\ y,t_1+s-\tau\bigr).
$$
Подстановка:
$$
Z\approx P(x,t_1+s)\iint\varphi(z)\,\varphi(y)\,P_2\bigl(z,t_1;\ y,t_1+s-\tau\bigr)\,dz\,dy=P(x,t_1+s)\cdot\mathbb E\Bigl[\varphi\bigl(x(t_1)\bigr)\,\varphi\bigl(x(t_1+s-\tau)\bigr)\Bigr].
$$
Обозначение: $w(t_1,s)=M_2(t_1,\,t_1+s-\tau)$, так что
$$
Z\bigl(x,s;\ t_1,\ t_1+s-\tau\bigr)\approx w(t_1,s)\,P(x,t_1+s).
$$
Выражение через $V$ по (7.5) с $b_1=t_1$, $b_2=t_1+s-\tau$: поздняя точка $V$ стоит в $t_1$, ранняя — в $t_1+s-\tau$, возраст $b_1-b_2=\tau-s$:
$$
w(t_1,s)=\int\varphi(x)\,V\bigl(x,\ \tau-s;\ t_1+s-\tau\bigr)\,dx .
$$
Проверка: $V(x,\tau-s;\,t_1+s-\tau)=\int\varphi(y)\,P_2\bigl(x,\ (t_1+s-\tau)+(\tau-s);\ y,\ t_1+s-\tau\bigr)\,dy=\int\varphi(y)\,P_2(x,t_1;\,y,t_1+s-\tau)\,dy$, и после умножения на $\varphi(x)$ и интегрирования по $x$ получается ровно $\mathbb E[\varphi(x(t_1))\varphi(x(t_1+s-\tau))]$.

### 7.6. Уровни 4 и 5

Та же схема, меняется только число ранних точек.

**Уровень 4:** обрываем $Y=F_3$ в уравнении для $Z(x,r;t_2,t_1)$, $u=t_2+r$:
$$
Y\bigl(x,r;\ t_2,t_1,\ t_2+r-\tau\bigr)\approx\Theta\bigl(t_2,\ t_1,\ t_2+r-\tau\bigr)\,P(x,t_2+r),\qquad
\Theta(t_2,t_1,t_0)=M_3(t_2,t_1,t_0)=\int\varphi(x)\,Z\bigl(x,\ t_2-t_1;\ t_1,t_0\bigr)\,dx .
$$

**Уровень 5:** обрываем $F_4$ в уравнении для $Y(x,q;t_3,t_2,t_1)$, $u=t_3+q$:
$$
F_4\bigl(x,u;\ t_3,t_2,t_1,\ u-\tau\bigr)\approx\Lambda\bigl(t_3,t_2,t_1,\ u-\tau\bigr)\,P(x,u),\qquad
\Lambda(t_3,t_2,t_1,t_0)=M_4(t_3,t_2,t_1,t_0)=\int\varphi(x)\,Y\bigl(x,\ t_3-t_2;\ t_2,t_1,t_0\bigr)\,dx .
$$

### Замкнутые системы

Во всех случаях $P(x,t)=P_{ex}(x,t)$ на $[0,\tau]$, функции с отрицательными моментами равны нулю.

**Уровень 3:**
$$
\begin{aligned}
&\partial_tP(x,t)=D\,\partial_x^2P(x,t)+\gamma\,\partial_xV(x,\tau;\,t-\tau),\\
&\partial_sV(x,s;t_1)=D\,\partial_x^2V(x,s;t_1)+\gamma\,w(t_1,s)\,\partial_xP(x,t_1+s),\qquad V(x,0;t_1)=\varphi(x)\,P(x,t_1),\\
&w(t_1,s)=\int\varphi(x)\,V(x,\tau-s;\,t_1-\tau+s)\,dx .
\end{aligned}
$$

**Уровень 4:** уравнения для $P$, $V$ — как в 6.4 (точные), и
$$
\begin{aligned}
&\partial_rZ(x,r;t_2,t_1)=D\,\partial_x^2Z+\gamma\,\Theta(t_2,t_1,\,t_2+r-\tau)\,\partial_xP(x,t_2+r),\qquad Z(x,0;t_2,t_1)=\varphi(x)\,V(x,t_2-t_1;\,t_1),\\
&\Theta(t_2,t_1,t_0)=\int\varphi(x)\,Z(x,\,t_2-t_1;\,t_1,t_0)\,dx .
\end{aligned}
$$

**Уровень 5:** уравнения для $P$, $V$, $Z$ — как в 6.4, и
$$
\begin{aligned}
&\partial_qY(x,q;t_3,t_2,t_1)=D\,\partial_x^2Y+\gamma\,\Lambda(t_3,t_2,t_1,\,t_3+q-\tau)\,\partial_xP(x,t_3+q),\quad Y(x,0;t_3,t_2,t_1)=\varphi(x)\,Z(x,t_3-t_2;\,t_2,t_1),\\
&\Lambda(t_3,t_2,t_1,t_0)=\int\varphi(x)\,Y(x,\,t_3-t_2;\,t_2,t_1,t_0)\,dx .
\end{aligned}
$$

---

## 8. Метод Канторовича (уровень 3)

### 8.1. Функционал

$$
\begin{aligned}
J={}&\int_\tau^T\!\!\int Q_0(x,t)\,\bigl[\partial_tP-D\,\partial_x^2P-\gamma\,\partial_xV(x,\tau;t-\tau)\bigr]\,dx\,dt+\int Q_0(x,\tau)\,\bigl[P(x,\tau)-P_{ex}(x,\tau)\bigr]\,dx\\
&+\iiint Q_1(x,s;t_1)\,\bigl[\partial_sV-D\,\partial_x^2V-\gamma\,w(t_1,s)\,\partial_xP(x,t_1+s)\bigr]\,dx\,ds\,dt_1+\iint Q_1(x,0;t_1)\,\bigl[V(x,0;t_1)-\varphi(x)P(x,t_1)\bigr]\,dx\,dt_1 .
\end{aligned}
$$
Условие $J=0$ при любых $Q_0$, $Q_1$ эквивалентно системе уровня 3 с начальными условиями.

### 8.2. Разложения

$$
P(x,t)=\sum_{k=1}^{n}h_k(x)\,g_k(t)\ \ (t\ge\tau),\qquad V(x,s;t_1)=\sum_{k=1}^{n}p_k(x)\,r_k(s;t_1).
$$

### 8.3. Варьирование по функциям от $x$

$g_k$, $r_k$ известны; $Q_0=\sum_i\delta h_i(x)\,g_i(t)$, $Q_1=\sum_i\delta p_i(x)\,r_i(s;t_1)$. Скобки $\langle\cdot,\cdot\rangle$ — интегралы по временным переменным. Из произвольности $\delta h_i$, $\delta p_i$:
$$
\sum_j\bigl(\langle g_i,\dot g_j\rangle+g_i(\tau)\,g_j(\tau)\bigr)\,h_j(x)-D\sum_j\langle g_i,g_j\rangle\,h_j''(x)-\gamma\sum_j\langle g_i(t),\,r_j(\tau;t-\tau)\rangle\,p_j'(x)=g_i(\tau)\,P_{ex}(x,\tau),
$$
$$
\begin{aligned}
&\sum_j\bigl(\langle r_i,\partial_sr_j\rangle+\langle r_i(0;t_1),r_j(0;t_1)\rangle\bigr)\,p_j(x)-D\sum_j\langle r_i,r_j\rangle\,p_j''(x)-\gamma\sum_j\langle r_i(s;t_1),\,w(t_1,s)\,g_j(t_1+s)\rangle\,h_j'(x)\\
&\qquad-\varphi(x)\sum_j\langle r_i(0;t_1),\,g_j(t_1)\rangle_{t_1\ge\tau}\,h_j(x)=\varphi(x)\int_0^\tau r_i(0;t_1)\,P_{ex}(x,t_1)\,dt_1,
\end{aligned}
$$
с граничными условиями $h_k(\pm L)=p_k(\pm L)=0$.

### 8.4. Варьирование по функциям времени

$h_k$, $p_k$ известны; $Q_0=\sum_ih_i(x)\,\delta g_i(t)$, $Q_1=\sum_ip_i(x)\,\delta r_i(s;t_1)$. Скобки — интегралы по $x$:
$$
\sum_j\langle h_i,h_j\rangle\,\dot g_j(t)=-D\sum_j\langle h_i',h_j'\rangle\,g_j(t)+\gamma\sum_j\langle h_i,p_j'\rangle\,r_j(\tau;t-\tau),\qquad\sum_j\langle h_i,h_j\rangle\,g_j(\tau)=\langle h_i,P_{ex}(\cdot,\tau)\rangle,
$$
$$
\sum_j\langle p_i,p_j\rangle\,\partial_sr_j(s;t_1)=-D\sum_j\langle p_i',p_j'\rangle\,r_j(s;t_1)+\gamma\,w(t_1,s)\sum_j\langle p_i,h_j'\rangle\,g_j(t_1+s),\qquad\sum_j\langle p_i,p_j\rangle\,r_j(0;t_1)=\sum_j\langle p_i,\varphi h_j\rangle\,g_j(t_1),
$$
где при $t_1<\tau$ в последнем условии $\sum_jh_jg_j(t_1)$ заменяется на $P_{ex}(x,t_1)$, и
$$
w(t_1,s)=\sum_j\langle\varphi,p_j\rangle\,r_j(\tau-s;\,t_1-\tau+s).
$$
Правые части относятся к прошедшему времени, поэтому задачи решаются одним проходом по $t$.

### 8.5. Итерации

Шаги 8.4 и 8.3 чередуются до сходимости $P(x,t)$, после шага 8.3 семейства $\{h_k\}$ и $\{p_k\}$ ортонормируются.

### 8.6. Уровни 4 и 5

Добавляются разложения $Z=\sum_kz_k(x)\,\zeta_k(r;t_2,t_1)$ и $Y=\sum_ky_k(x)\,\eta_k(q;t_3,t_2,t_1)$. В общей записи $F_m=\sum_kf_{m,k}(x)\,c_{m,k}(a;\bar t_m)$ уравнения имеют вид:

*по $x$:*
$$
\sum_j\bigl(\langle c_{m,i},\partial_ac_{m,j}\rangle+\langle c_{m,i},c_{m,j}\rangle'\bigr)f_{m,j}-D\sum_j\langle c_{m,i},c_{m,j}\rangle f_{m,j}''-\gamma\sum_j\langle c_{m,i},\sigma_{m,j}\rangle\,\psi_{m,j}'-\varphi\sum_j\langle c_{m,i},c_{m-1,j}\rangle'f_{m-1,j}=\text{(правая часть при }m=0,1),
$$
*по времени:*
$$
\sum_j\langle f_{m,i},f_{m,j}\rangle\,\partial_ac_{m,j}=-D\sum_j\langle f_{m,i}',f_{m,j}'\rangle\,c_{m,j}+\gamma\sum_j\langle f_{m,i},\psi_{m,j}'\rangle\,\sigma_{m,j},\qquad\sum_j\langle f_{m,i},f_{m,j}\rangle\,c_{m,j}(0)=\sum_j\langle f_{m,i},\varphi f_{m-1,j}\rangle\,c_{m-1,j},
$$
где $\langle\cdot,\cdot\rangle'$ — интеграл при $a=0$. Источник $\sigma_{m,j}\,\psi_{m,j}(x)$ равен $c_{m+1,j}(a;\bar t_m,u-\tau)\,f_{m+1,j}(x)$ для $m<L-2$ и $M_{L-1}\,g_j(u)\,h_j(x)$ для последнего уравнения.

---

## 9. Предположения

Используются стандартные условия: плотности $P_n$ существуют, гладкие по $x$ и убывают на $\pm\infty$, а дифференцирование по времени перестановочно со средним. Все уравнения разделов 5–6 точны при этих условиях. Единственное модельное приближение — гипотеза обрыва раздела 7.
