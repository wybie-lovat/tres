"""Minifigure, horse and rider assemblies (LDraw sub-models)."""
import numpy as np
from lego import COLORS, rot_x, rot_z, rot_yd

def _c(col):
    return COLORS[col][0] if isinstance(col, str) else col

def _line(color, pos, M, part):
    f = lambda v: ('%.3f' % v).rstrip('0').rstrip('.') if abs(v) > 1e-9 else '0'
    vals = list(pos) + [M[0, 0], M[0, 1], M[0, 2], M[1, 0], M[1, 1], M[1, 2], M[2, 0], M[2, 1], M[2, 2]]
    fn = part if part.endswith(('.dat', '.ldr')) else part + '.dat'
    return f'1 {_c(color)} ' + ' '.join(f(v) for v in vals) + f' {fn}'

HAND_REL = np.array([5.0, 18.88, -9.88])


class Fig:
    """A minifigure description. Items are (part, color). Arm angles in degrees (negative = raised forward)."""

    def __init__(self, name, torso, legs, head='3626bp01', headgear=None, arms=None, hands='yellow',
                 torso_part='973', neck=None, back=None, left=None, right=None, arm_l=-10, arm_r=-10,
                 sit=False, short=False, skin='yellow', left_rot=None, right_rot=None, visor=None, face_col=None,
                 extras=()):
        self.name = name
        self.torso, self.legs, self.head = torso, legs, head
        self.headgear, self.arms, self.hands = headgear, arms or torso, hands
        self.torso_part, self.neck, self.back = torso_part, neck, back
        self.left, self.right = left, right
        self.arm_l, self.arm_r, self.sit, self.short = arm_l, arm_r, sit, short
        self.skin = skin
        self.left_rot, self.right_rot = left_rot, right_rot
        self.visor = visor
        self.extras = extras   # [(part, colour, 'r'|'l', offset(3), rot(3x3))] attached to a hand item

    def parts(self):
        """List of (part, color, pos, M) relative to the figure origin (between the feet, on the ground)."""
        T = np.array([0, -72.0, 0]) if not self.short else np.array([0, -56.0, 0])
        if self.sit:
            T = np.array([0, -52.0, 0])
        I = np.eye(3)
        out = []
        out.append((self.torso_part, self.torso, T, I))
        out.append((self.head, self.skin, T + [0, -24, 0], I))
        if self.headgear:
            out.append((self.headgear[0], self.headgear[1], T + [0, -24, 0], I))
        if self.visor:
            out.append((self.visor[0], self.visor[1], T + [0, -24, 0], I))
        if self.neck:
            out.append((self.neck[0], self.neck[1], T, I))
        if self.back:
            out.append((self.back[0], self.back[1], T, I))
        if self.short:
            out.append(('41879a', self.legs, T + [0, 32, 0], I))
        elif self.sit:
            out.append(('73200-f2', self.legs, T + [0, 32, 0], I))
        else:
            out.append(('3815b', self.legs, T + [0, 32, 0], I))
            out.append(('3816b', self.legs, T + [0, 44, 0], I))
            out.append(('3817b', self.legs, T + [0, 44, 0], I))
        for side, part, ang, item, irot in ((1, '3819', self.arm_l, self.left, self.left_rot),
                                            (-1, '3818', self.arm_r, self.right, self.right_rot)):
            A = rot_z(-10 * side) @ rot_x(ang)
            P = T + np.array([15.552 * side, 9, 0])
            out.append((part, self.arms, P, A))
            H = A @ rot_x(45)
            PH = P + A @ (HAND_REL * [side, 1, 1])
            out.append(('3820', self.hands, PH, H))
            if item:
                R = H @ (irot if irot is not None else np.eye(3))
                out.append((item[0], item[1], PH, R))
                for (part2, col2, hand, off, rot2) in self.extras:
                    if (hand == 'l') == (side == 1):
                        out.append((part2, col2, PH + R @ np.array(off, dtype=float), R @ rot2))
        return out

    def ldraw(self):
        lines = [f'0 {self.name}', f'0 Name: {self.name}.ldr', '0 Author: Nobles & Common Folk at Quarrel generator', '']
        for part, col, pos, M in self.parts():
            lines.append(_line(col, pos, M, part))
        return lines


def horse_parts(color, saddle='black', barding=None, head_armor=None, rider=None):
    """Horse standing on the ground; origin between the front and back hooves on the ground."""
    I = np.eye(3)
    H = np.array([0, -57.0, 0])
    out = [('4493c00', color, H, I)]
    out.append(('4491b', saddle, H + [0, -8, 0], I))
    if barding:
        out.append(('2490', barding, H + [0, 0, 0], I))
    if head_armor:
        out.append(('48492', head_armor, H + [0, 0, 0], I))
    return out
