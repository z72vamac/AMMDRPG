\ Model PD-Stages
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  dRLt[0] + dRLt[1] + dRLt[2] + dLRt[0] + dLRt[1] + dLRt[2] + dLRt[3]
   + 0 deltat[0] + 0 deltat[1] + 0 deltat[2] + 0 deltat[3] + 0 zetat[0]
   + 0 zetat[1] + 0 zetat[2] + 0 zetat[3]
Subject To
 R0: uigtd[101,1,1,0] + uigtd[101,2,1,0] <= 1
 R1: uigtd[101,1,1,1] + uigtd[101,2,1,1] <= 1
 R2: uigtd[101,1,2,0] + uigtd[101,2,2,0] <= 1
 R3: uigtd[101,1,2,1] + uigtd[101,2,2,1] <= 1
 R4: vigtd[101,1,1,0] + vigtd[101,2,1,0] <= 1
 R5: vigtd[101,1,1,1] + vigtd[101,2,1,1] <= 1
 R6: vigtd[101,1,2,0] + vigtd[101,2,2,0] <= 1
 R7: vigtd[101,1,2,1] + vigtd[101,2,2,1] <= 1
 R8: uigtd[101,1,1,0] + uigtd[101,1,1,1] + uigtd[101,1,2,0]
   + uigtd[101,1,2,1] = 1
 R9: uigtd[101,2,1,0] + uigtd[101,2,1,1] + uigtd[101,2,2,0]
   + uigtd[101,2,2,1] = 1
 R10: vigtd[101,1,1,0] + vigtd[101,1,1,1] + vigtd[101,1,2,0]
   + vigtd[101,1,2,1] = 1
 R11: vigtd[101,2,1,0] + vigtd[101,2,1,1] + vigtd[101,2,2,0]
   + vigtd[101,2,2,1] = 1
 R12: betat[1] - betat[2] <= 0
 R13: betat[2] - betat[3] <= 0
 R14: - 2 betat[1] >= 0
 R15: uigtd[101,1,1,0] + uigtd[101,1,1,1] + uigtd[101,2,1,0]
   + uigtd[101,2,1,1] - 2 betat[2] >= 0
 R16: betat[0] >= 1
 R17: uigtd[101,1,1,0] + uigtd[101,1,1,1] + uigtd[101,2,1,0]
   + uigtd[101,2,1,1] + betat[1] >= 1
 R18: uigtd[101,1,2,0] + uigtd[101,1,2,1] + uigtd[101,2,2,0]
   + uigtd[101,2,2,1] + betat[2] >= 1
 R19: betat[3] >= 1
 R20: - uigtd[101,1,1,0] - uigtd[101,1,1,1] - uigtd[101,1,2,0]
   - uigtd[101,1,2,1] + muig[101,1] = 0
 R21: - uigtd[101,2,1,0] - uigtd[101,2,1,1] - uigtd[101,2,2,0]
   - uigtd[101,2,2,1] + muig[101,2] = 0
 R22: - vigtd[101,1,1,0] - vigtd[101,1,1,1] - vigtd[101,1,2,0]
   - vigtd[101,1,2,1] + muig[101,1] = 0
 R23: - vigtd[101,2,1,0] - vigtd[101,2,1,1] - vigtd[101,2,2,0]
   - vigtd[101,2,2,1] + muig[101,2] = 0
 R24: uigtd[101,1,1,0] - vigtd[101,1,1,0] = 0
 R25: uigtd[101,1,1,1] - vigtd[101,1,1,1] = 0
 R26: uigtd[101,2,1,0] - vigtd[101,2,1,0] = 0
 R27: uigtd[101,2,1,1] - vigtd[101,2,1,1] = 0
 R28: uigtd[101,1,2,0] - vigtd[101,1,2,0] = 0
 R29: uigtd[101,1,2,1] - vigtd[101,1,2,1] = 0
 R30: uigtd[101,2,2,0] - vigtd[101,2,2,0] = 0
 R31: uigtd[101,2,2,1] - vigtd[101,2,2,1] = 0
 R32: - muig[101,1] + pig[101,1] - alphaig[101,1] >= -1
 R33: - muig[101,2] + pig[101,2] - alphaig[101,2] >= -1
 R34: - muig[101,1] + pig[101,1] <= 0
 R35: - muig[101,2] + pig[101,2] <= 0
 R36: pig[101,1] - alphaig[101,1] <= 0
 R37: pig[101,2] - alphaig[101,2] <= 0
 R38: sig[101,1] >= 0
 R39: sig[101,1] <= 0
 R40: sig[101,2] >= 0
 R41: sig[101,2] <= 0
 R42: - uigtd[101,1,1,0] + uigtd[101,1,1,1] - uigtd[101,1,2,0]
   - uigtd[101,2,1,0] - uigtd[101,2,2,0] <= 0
 R43: - uigtd[101,1,1,0] - uigtd[101,1,2,0] + uigtd[101,1,2,1]
   - uigtd[101,2,1,0] - uigtd[101,2,2,0] <= 0
 R44: - uigtd[101,1,1,0] - uigtd[101,1,2,0] - uigtd[101,2,1,0]
   + uigtd[101,2,1,1] - uigtd[101,2,2,0] <= 0
 R45: - uigtd[101,1,1,0] - uigtd[101,1,2,0] - uigtd[101,2,1,0]
   - uigtd[101,2,2,0] + uigtd[101,2,2,1] <= 0
 R46: - vigtd[101,1,1,0] + vigtd[101,1,1,1] - vigtd[101,1,2,0]
   - vigtd[101,2,1,0] - vigtd[101,2,2,0] <= 0
 R47: - vigtd[101,1,1,0] - vigtd[101,1,2,0] + vigtd[101,1,2,1]
   - vigtd[101,2,1,0] - vigtd[101,2,2,0] <= 0
 R48: - vigtd[101,1,1,0] - vigtd[101,1,2,0] - vigtd[101,2,1,0]
   + vigtd[101,2,1,1] - vigtd[101,2,2,0] <= 0
 R49: - vigtd[101,1,1,0] - vigtd[101,1,2,0] - vigtd[101,2,1,0]
   - vigtd[101,2,2,0] + vigtd[101,2,2,1] <= 0
 R50: difLigtd[101,1,1,0,0] - xLt[1,0] + Rig[101,1,0] >= 0
 R51: difLigtd[101,1,1,0,1] - xLt[1,1] + Rig[101,1,1] >= 0
 R52: difLigtd[101,1,1,1,0] - xLt[1,0] + Rig[101,1,0] >= 0
 R53: difLigtd[101,1,1,1,1] - xLt[1,1] + Rig[101,1,1] >= 0
 R54: difLigtd[101,1,2,0,0] - xLt[2,0] + Rig[101,1,0] >= 0
 R55: difLigtd[101,1,2,0,1] - xLt[2,1] + Rig[101,1,1] >= 0
 R56: difLigtd[101,1,2,1,0] - xLt[2,0] + Rig[101,1,0] >= 0
 R57: difLigtd[101,1,2,1,1] - xLt[2,1] + Rig[101,1,1] >= 0
 R58: difLigtd[101,2,1,0,0] - xLt[1,0] + Rig[101,2,0] >= 0
 R59: difLigtd[101,2,1,0,1] - xLt[1,1] + Rig[101,2,1] >= 0
 R60: difLigtd[101,2,1,1,0] - xLt[1,0] + Rig[101,2,0] >= 0
 R61: difLigtd[101,2,1,1,1] - xLt[1,1] + Rig[101,2,1] >= 0
 R62: difLigtd[101,2,2,0,0] - xLt[2,0] + Rig[101,2,0] >= 0
 R63: difLigtd[101,2,2,0,1] - xLt[2,1] + Rig[101,2,1] >= 0
 R64: difLigtd[101,2,2,1,0] - xLt[2,0] + Rig[101,2,0] >= 0
 R65: difLigtd[101,2,2,1,1] - xLt[2,1] + Rig[101,2,1] >= 0
 R66: difLigtd[101,1,1,0,0] + xLt[1,0] - Rig[101,1,0] >= 0
 R67: difLigtd[101,1,1,0,1] + xLt[1,1] - Rig[101,1,1] >= 0
 R68: difLigtd[101,1,1,1,0] + xLt[1,0] - Rig[101,1,0] >= 0
 R69: difLigtd[101,1,1,1,1] + xLt[1,1] - Rig[101,1,1] >= 0
 R70: difLigtd[101,1,2,0,0] + xLt[2,0] - Rig[101,1,0] >= 0
 R71: difLigtd[101,1,2,0,1] + xLt[2,1] - Rig[101,1,1] >= 0
 R72: difLigtd[101,1,2,1,0] + xLt[2,0] - Rig[101,1,0] >= 0
 R73: difLigtd[101,1,2,1,1] + xLt[2,1] - Rig[101,1,1] >= 0
 R74: difLigtd[101,2,1,0,0] + xLt[1,0] - Rig[101,2,0] >= 0
 R75: difLigtd[101,2,1,0,1] + xLt[1,1] - Rig[101,2,1] >= 0
 R76: difLigtd[101,2,1,1,0] + xLt[1,0] - Rig[101,2,0] >= 0
 R77: difLigtd[101,2,1,1,1] + xLt[1,1] - Rig[101,2,1] >= 0
 R78: difLigtd[101,2,2,0,0] + xLt[2,0] - Rig[101,2,0] >= 0
 R79: difLigtd[101,2,2,0,1] + xLt[2,1] - Rig[101,2,1] >= 0
 R80: difLigtd[101,2,2,1,0] + xLt[2,0] - Rig[101,2,0] >= 0
 R81: difLigtd[101,2,2,1,1] + xLt[2,1] - Rig[101,2,1] >= 0
 R82: - 10000 uigtd[101,1,1,0] + pLigtd[101,1,1,0] <= 0
 R83: - 10000 uigtd[101,1,1,1] + pLigtd[101,1,1,1] <= 0
 R84: - 10000 uigtd[101,1,2,0] + pLigtd[101,1,2,0] <= 0
 R85: - 10000 uigtd[101,1,2,1] + pLigtd[101,1,2,1] <= 0
 R86: - 10000 uigtd[101,2,1,0] + pLigtd[101,2,1,0] <= 0
 R87: - 10000 uigtd[101,2,1,1] + pLigtd[101,2,1,1] <= 0
 R88: - 10000 uigtd[101,2,2,0] + pLigtd[101,2,2,0] <= 0
 R89: - 10000 uigtd[101,2,2,1] + pLigtd[101,2,2,1] <= 0
 R90: - dLigtd[101,1,1,0] + pLigtd[101,1,1,0] <= 0
 R91: - dLigtd[101,1,1,1] + pLigtd[101,1,1,1] <= 0
 R92: - dLigtd[101,1,2,0] + pLigtd[101,1,2,0] <= 0
 R93: - dLigtd[101,1,2,1] + pLigtd[101,1,2,1] <= 0
 R94: - dLigtd[101,2,1,0] + pLigtd[101,2,1,0] <= 0
 R95: - dLigtd[101,2,1,1] + pLigtd[101,2,1,1] <= 0
 R96: - dLigtd[101,2,2,0] + pLigtd[101,2,2,0] <= 0
 R97: - dLigtd[101,2,2,1] + pLigtd[101,2,2,1] <= 0
 R98: pLigtd[101,1,1,0] >= 0
 R99: pLigtd[101,1,1,1] >= 0
 R100: pLigtd[101,1,2,0] >= 0
 R101: pLigtd[101,1,2,1] >= 0
 R102: pLigtd[101,2,1,0] >= 0
 R103: pLigtd[101,2,1,1] >= 0
 R104: pLigtd[101,2,2,0] >= 0
 R105: pLigtd[101,2,2,1] >= 0
 R106: - 10000 uigtd[101,1,1,0] - dLigtd[101,1,1,0] + pLigtd[101,1,1,0]
   >= -10000
 R107: - 10000 uigtd[101,1,1,1] - dLigtd[101,1,1,1] + pLigtd[101,1,1,1]
   >= -10000
 R108: - 10000 uigtd[101,1,2,0] - dLigtd[101,1,2,0] + pLigtd[101,1,2,0]
   >= -10000
 R109: - 10000 uigtd[101,1,2,1] - dLigtd[101,1,2,1] + pLigtd[101,1,2,1]
   >= -10000
 R110: - 10000 uigtd[101,2,1,0] - dLigtd[101,2,1,0] + pLigtd[101,2,1,0]
   >= -10000
 R111: - 10000 uigtd[101,2,1,1] - dLigtd[101,2,1,1] + pLigtd[101,2,1,1]
   >= -10000
 R112: - 10000 uigtd[101,2,2,0] - dLigtd[101,2,2,0] + pLigtd[101,2,2,0]
   >= -10000
 R113: - 10000 uigtd[101,2,2,1] - dLigtd[101,2,2,1] + pLigtd[101,2,2,1]
   >= -10000
 R114: difRigtd[101,1,1,0,0] + xRt[1,0] - Lig[101,1,0] >= 0
 R115: difRigtd[101,1,1,0,1] + xRt[1,1] - Lig[101,1,1] >= 0
 R116: difRigtd[101,1,1,1,0] + xRt[1,0] - Lig[101,1,0] >= 0
 R117: difRigtd[101,1,1,1,1] + xRt[1,1] - Lig[101,1,1] >= 0
 R118: difRigtd[101,1,2,0,0] + xRt[2,0] - Lig[101,1,0] >= 0
 R119: difRigtd[101,1,2,0,1] + xRt[2,1] - Lig[101,1,1] >= 0
 R120: difRigtd[101,1,2,1,0] + xRt[2,0] - Lig[101,1,0] >= 0
 R121: difRigtd[101,1,2,1,1] + xRt[2,1] - Lig[101,1,1] >= 0
 R122: difRigtd[101,2,1,0,0] + xRt[1,0] - Lig[101,2,0] >= 0
 R123: difRigtd[101,2,1,0,1] + xRt[1,1] - Lig[101,2,1] >= 0
 R124: difRigtd[101,2,1,1,0] + xRt[1,0] - Lig[101,2,0] >= 0
 R125: difRigtd[101,2,1,1,1] + xRt[1,1] - Lig[101,2,1] >= 0
 R126: difRigtd[101,2,2,0,0] + xRt[2,0] - Lig[101,2,0] >= 0
 R127: difRigtd[101,2,2,0,1] + xRt[2,1] - Lig[101,2,1] >= 0
 R128: difRigtd[101,2,2,1,0] + xRt[2,0] - Lig[101,2,0] >= 0
 R129: difRigtd[101,2,2,1,1] + xRt[2,1] - Lig[101,2,1] >= 0
 R130: difRigtd[101,1,1,0,0] - xRt[1,0] + Lig[101,1,0] >= 0
 R131: difRigtd[101,1,1,0,1] - xRt[1,1] + Lig[101,1,1] >= 0
 R132: difRigtd[101,1,1,1,0] - xRt[1,0] + Lig[101,1,0] >= 0
 R133: difRigtd[101,1,1,1,1] - xRt[1,1] + Lig[101,1,1] >= 0
 R134: difRigtd[101,1,2,0,0] - xRt[2,0] + Lig[101,1,0] >= 0
 R135: difRigtd[101,1,2,0,1] - xRt[2,1] + Lig[101,1,1] >= 0
 R136: difRigtd[101,1,2,1,0] - xRt[2,0] + Lig[101,1,0] >= 0
 R137: difRigtd[101,1,2,1,1] - xRt[2,1] + Lig[101,1,1] >= 0
 R138: difRigtd[101,2,1,0,0] - xRt[1,0] + Lig[101,2,0] >= 0
 R139: difRigtd[101,2,1,0,1] - xRt[1,1] + Lig[101,2,1] >= 0
 R140: difRigtd[101,2,1,1,0] - xRt[1,0] + Lig[101,2,0] >= 0
 R141: difRigtd[101,2,1,1,1] - xRt[1,1] + Lig[101,2,1] >= 0
 R142: difRigtd[101,2,2,0,0] - xRt[2,0] + Lig[101,2,0] >= 0
 R143: difRigtd[101,2,2,0,1] - xRt[2,1] + Lig[101,2,1] >= 0
 R144: difRigtd[101,2,2,1,0] - xRt[2,0] + Lig[101,2,0] >= 0
 R145: difRigtd[101,2,2,1,1] - xRt[2,1] + Lig[101,2,1] >= 0
 R146: - 10000 vigtd[101,1,1,0] + pRigtd[101,1,1,0] <= 0
 R147: - 10000 vigtd[101,1,1,1] + pRigtd[101,1,1,1] <= 0
 R148: - 10000 vigtd[101,1,2,0] + pRigtd[101,1,2,0] <= 0
 R149: - 10000 vigtd[101,1,2,1] + pRigtd[101,1,2,1] <= 0
 R150: - 10000 vigtd[101,2,1,0] + pRigtd[101,2,1,0] <= 0
 R151: - 10000 vigtd[101,2,1,1] + pRigtd[101,2,1,1] <= 0
 R152: - 10000 vigtd[101,2,2,0] + pRigtd[101,2,2,0] <= 0
 R153: - 10000 vigtd[101,2,2,1] + pRigtd[101,2,2,1] <= 0
 R154: - dRigtd[101,1,1,0] + pRigtd[101,1,1,0] <= 0
 R155: - dRigtd[101,1,1,1] + pRigtd[101,1,1,1] <= 0
 R156: - dRigtd[101,1,2,0] + pRigtd[101,1,2,0] <= 0
 R157: - dRigtd[101,1,2,1] + pRigtd[101,1,2,1] <= 0
 R158: - dRigtd[101,2,1,0] + pRigtd[101,2,1,0] <= 0
 R159: - dRigtd[101,2,1,1] + pRigtd[101,2,1,1] <= 0
 R160: - dRigtd[101,2,2,0] + pRigtd[101,2,2,0] <= 0
 R161: - dRigtd[101,2,2,1] + pRigtd[101,2,2,1] <= 0
 R162: pRigtd[101,1,1,0] >= 0
 R163: pRigtd[101,1,1,1] >= 0
 R164: pRigtd[101,1,2,0] >= 0
 R165: pRigtd[101,1,2,1] >= 0
 R166: pRigtd[101,2,1,0] >= 0
 R167: pRigtd[101,2,1,1] >= 0
 R168: pRigtd[101,2,2,0] >= 0
 R169: pRigtd[101,2,2,1] >= 0
 R170: - 10000 vigtd[101,1,1,0] - dRigtd[101,1,1,0] + pRigtd[101,1,1,0]
   >= -10000
 R171: - 10000 vigtd[101,1,1,1] - dRigtd[101,1,1,1] + pRigtd[101,1,1,1]
   >= -10000
 R172: - 10000 vigtd[101,1,2,0] - dRigtd[101,1,2,0] + pRigtd[101,1,2,0]
   >= -10000
 R173: - 10000 vigtd[101,1,2,1] - dRigtd[101,1,2,1] + pRigtd[101,1,2,1]
   >= -10000
 R174: - 10000 vigtd[101,2,1,0] - dRigtd[101,2,1,0] + pRigtd[101,2,1,0]
   >= -10000
 R175: - 10000 vigtd[101,2,1,1] - dRigtd[101,2,1,1] + pRigtd[101,2,1,1]
   >= -10000
 R176: - 10000 vigtd[101,2,2,0] - dRigtd[101,2,2,0] + pRigtd[101,2,2,0]
   >= -10000
 R177: - 10000 vigtd[101,2,2,1] - dRigtd[101,2,2,1] + pRigtd[101,2,2,1]
   >= -10000
 error[0,0]: difRLt[0,0] + xLt[1,0] - xRt[0,0] >= 0
 error[0,1]: difRLt[0,1] + xLt[1,1] - xRt[0,1] >= 0
 error[1,0]: difRLt[1,0] + xLt[2,0] - xRt[1,0] >= 0
 error[1,1]: difRLt[1,1] + xLt[2,1] - xRt[1,1] >= 0
 error[2,0]: difRLt[2,0] + xLt[3,0] - xRt[2,0] >= 0
 error[2,1]: difRLt[2,1] + xLt[3,1] - xRt[2,1] >= 0
 error2[0,0]: difRLt[0,0] - xLt[1,0] + xRt[0,0] >= 0
 error2[0,1]: difRLt[0,1] - xLt[1,1] + xRt[0,1] >= 0
 error2[1,0]: difRLt[1,0] - xLt[2,0] + xRt[1,0] >= 0
 error2[1,1]: difRLt[1,1] - xLt[2,1] + xRt[1,1] >= 0
 error2[2,0]: difRLt[2,0] - xLt[3,0] + xRt[2,0] >= 0
 error2[2,1]: difRLt[2,1] - xLt[3,1] + xRt[2,1] >= 0
 R190: difLRt[0,0] - xLt[0,0] + xRt[0,0] >= 0
 R191: difLRt[0,1] - xLt[0,1] + xRt[0,1] >= 0
 R192: difLRt[1,0] - xLt[1,0] + xRt[1,0] >= 0
 R193: difLRt[1,1] - xLt[1,1] + xRt[1,1] >= 0
 R194: difLRt[2,0] - xLt[2,0] + xRt[2,0] >= 0
 R195: difLRt[2,1] - xLt[2,1] + xRt[2,1] >= 0
 R196: difLRt[3,0] - xLt[3,0] + xRt[3,0] >= 0
 R197: difLRt[3,1] - xLt[3,1] + xRt[3,1] >= 0
 R198: difLRt[0,0] + xLt[0,0] - xRt[0,0] >= 0
 R199: difLRt[0,1] + xLt[0,1] - xRt[0,1] >= 0
 R200: difLRt[1,0] + xLt[1,0] - xRt[1,0] >= 0
 R201: difLRt[1,1] + xLt[1,1] - xRt[1,1] >= 0
 R202: difLRt[2,0] + xLt[2,0] - xRt[2,0] >= 0
 R203: difLRt[2,1] + xLt[2,1] - xRt[2,1] >= 0
 R204: difLRt[3,0] + xLt[3,0] - xRt[3,0] >= 0
 R205: difLRt[3,1] + xLt[3,1] - xRt[3,1] >= 0
 R206: 3 uigtd[101,1,1,0] + 0.2 pLigtd[101,1,1,0] + 0.2 pRigtd[101,1,1,0]
   - dLRt[1] + 2e-06 pig[101,1] <= 3
 R207: 3 uigtd[101,1,1,1] + 0.2 pLigtd[101,1,1,1] + 0.2 pRigtd[101,1,1,1]
   - dLRt[1] + 2e-06 pig[101,1] <= 3
 R208: 3 uigtd[101,2,1,0] + 0.2 pLigtd[101,2,1,0] + 0.2 pRigtd[101,2,1,0]
   - dLRt[1] + 2e-06 pig[101,2] <= 3
 R209: 3 uigtd[101,2,1,1] + 0.2 pLigtd[101,2,1,1] + 0.2 pRigtd[101,2,1,1]
   - dLRt[1] + 2e-06 pig[101,2] <= 3
 R210: 3 uigtd[101,1,2,0] + 0.2 pLigtd[101,1,2,0] + 0.2 pRigtd[101,1,2,0]
   - dLRt[2] + 2e-06 pig[101,1] <= 3
 R211: 3 uigtd[101,1,2,1] + 0.2 pLigtd[101,1,2,1] + 0.2 pRigtd[101,1,2,1]
   - dLRt[2] + 2e-06 pig[101,1] <= 3
 R212: 3 uigtd[101,2,2,0] + 0.2 pLigtd[101,2,2,0] + 0.2 pRigtd[101,2,2,0]
   - dLRt[2] + 2e-06 pig[101,2] <= 3
 R213: 3 uigtd[101,2,2,1] + 0.2 pLigtd[101,2,2,1] + 0.2 pRigtd[101,2,2,1]
   - dLRt[2] + 2e-06 pig[101,2] <= 3
 R214: dLRt[1] <= 3
 R215: dLRt[2] <= 3
 R216: rhoig[101,1] - landaig[101,1] + minig[101,1] - maxig[101,1] = 0
 R217: minig[101,1] + maxig[101,1] - alphaig[101,1] = 0
 R218: maxig[101,1] + entryig[101,1] <= 1
 R219: minig[101,1] - entryig[101,1] <= 0
 R220: Rig[101,1,0] = 11
 R221: Rig[101,1,1] + 1e-05 rhoig[101,1] = 20.00001
 R222: Lig[101,1,0] = 11
 R223: Lig[101,1,1] + 1e-05 landaig[101,1] = 20.00001
 R224: rhoig[101,2] - landaig[101,2] + minig[101,2] - maxig[101,2] = 0
 R225: minig[101,2] + maxig[101,2] - alphaig[101,2] = 0
 R226: maxig[101,2] + entryig[101,2] <= 1
 R227: minig[101,2] - entryig[101,2] <= 0
 R228: Rig[101,2,0] = 13
 R229: Rig[101,2,1] + 1e-05 rhoig[101,2] = 20.00001
 R230: Lig[101,2,0] = 13
 R231: Lig[101,2,1] + 1e-05 landaig[101,2] = 20.00001
 R232: 1e-05 pig[101,1] = 1e-11
 R233: 1e-05 pig[101,2] = 1e-11
 R234: xLt[0,0] = 0
 R235: xLt[0,1] = 5
 R236: xRt[0,0] = 0
 R237: xRt[0,1] = 5
 R238: xLt[3,0] = 20
 R239: xLt[3,1] = 5
 R240: xRt[3,0] = 20
 R241: xRt[3,1] = 5
 difLigtd[101,1,1,0]: [ - dLigtd[101,1,1,0] ^2 + difLigtd[101,1,1,0,0] ^2
   + difLigtd[101,1,1,0,1] ^2 ] <= 0
 difLigtd[101,1,1,1]: [ - dLigtd[101,1,1,1] ^2 + difLigtd[101,1,1,1,0] ^2
   + difLigtd[101,1,1,1,1] ^2 ] <= 0
 difLigtd[101,1,2,0]: [ - dLigtd[101,1,2,0] ^2 + difLigtd[101,1,2,0,0] ^2
   + difLigtd[101,1,2,0,1] ^2 ] <= 0
 difLigtd[101,1,2,1]: [ - dLigtd[101,1,2,1] ^2 + difLigtd[101,1,2,1,0] ^2
   + difLigtd[101,1,2,1,1] ^2 ] <= 0
 difLigtd[101,2,1,0]: [ - dLigtd[101,2,1,0] ^2 + difLigtd[101,2,1,0,0] ^2
   + difLigtd[101,2,1,0,1] ^2 ] <= 0
 difLigtd[101,2,1,1]: [ - dLigtd[101,2,1,1] ^2 + difLigtd[101,2,1,1,0] ^2
   + difLigtd[101,2,1,1,1] ^2 ] <= 0
 difLigtd[101,2,2,0]: [ - dLigtd[101,2,2,0] ^2 + difLigtd[101,2,2,0,0] ^2
   + difLigtd[101,2,2,0,1] ^2 ] <= 0
 difLigtd[101,2,2,1]: [ - dLigtd[101,2,2,1] ^2 + difLigtd[101,2,2,1,0] ^2
   + difLigtd[101,2,2,1,1] ^2 ] <= 0
 difRigtd[101,1,1,0]: [ - dRigtd[101,1,1,0] ^2 + difRigtd[101,1,1,0,0] ^2
   + difRigtd[101,1,1,0,1] ^2 ] <= 0
 difRigtd[101,1,1,1]: [ - dRigtd[101,1,1,1] ^2 + difRigtd[101,1,1,1,0] ^2
   + difRigtd[101,1,1,1,1] ^2 ] <= 0
 difRigtd[101,1,2,0]: [ - dRigtd[101,1,2,0] ^2 + difRigtd[101,1,2,0,0] ^2
   + difRigtd[101,1,2,0,1] ^2 ] <= 0
 difRigtd[101,1,2,1]: [ - dRigtd[101,1,2,1] ^2 + difRigtd[101,1,2,1,0] ^2
   + difRigtd[101,1,2,1,1] ^2 ] <= 0
 difRigtd[101,2,1,0]: [ - dRigtd[101,2,1,0] ^2 + difRigtd[101,2,1,0,0] ^2
   + difRigtd[101,2,1,0,1] ^2 ] <= 0
 difRigtd[101,2,1,1]: [ - dRigtd[101,2,1,1] ^2 + difRigtd[101,2,1,1,0] ^2
   + difRigtd[101,2,1,1,1] ^2 ] <= 0
 difRigtd[101,2,2,0]: [ - dRigtd[101,2,2,0] ^2 + difRigtd[101,2,2,0,0] ^2
   + difRigtd[101,2,2,0,1] ^2 ] <= 0
 difRigtd[101,2,2,1]: [ - dRigtd[101,2,2,1] ^2 + difRigtd[101,2,2,1,0] ^2
   + difRigtd[101,2,2,1,1] ^2 ] <= 0
 difRLt[0]: [ - dRLt[0] ^2 + difRLt[0,0] ^2 + difRLt[0,1] ^2 ] <= 0
 difRLt[1]: [ - dRLt[1] ^2 + difRLt[1,0] ^2 + difRLt[1,1] ^2 ] <= 0
 difRLt[2]: [ - dRLt[2] ^2 + difRLt[2,0] ^2 + difRLt[2,1] ^2 ] <= 0
 difLRt[0]: [ - dLRt[0] ^2 + difLRt[0,0] ^2 + difLRt[0,1] ^2 ] <= 0
 difLRt[1]: [ - dLRt[1] ^2 + difLRt[1,0] ^2 + difLRt[1,1] ^2 ] <= 0
 difLRt[2]: [ - dLRt[2] ^2 + difLRt[2,0] ^2 + difLRt[2,1] ^2 ] <= 0
 difLRt[3]: [ - dLRt[3] ^2 + difLRt[3,0] ^2 + difLRt[3,1] ^2 ] <= 0
Bounds
 deltat[0] <= 1
 deltat[1] <= 1
 deltat[2] <= 1
 deltat[3] <= 1
 rhoig[101,1] <= 1
 rhoig[101,2] <= 1
 landaig[101,1] <= 1
 landaig[101,2] <= 1
 minig[101,1] <= 1
 minig[101,2] <= 1
 maxig[101,1] <= 1
 maxig[101,2] <= 1
 pig[101,1] <= 1
 pig[101,2] <= 1
 alphaig[101,1] <= 1
 alphaig[101,2] <= 1
Binaries
 uigtd[101,1,1,0] uigtd[101,1,1,1] uigtd[101,1,2,0] uigtd[101,1,2,1]
 uigtd[101,2,1,0] uigtd[101,2,1,1] uigtd[101,2,2,0] uigtd[101,2,2,1]
 vigtd[101,1,1,0] vigtd[101,1,1,1] vigtd[101,1,2,0] vigtd[101,1,2,1]
 vigtd[101,2,1,0] vigtd[101,2,1,1] vigtd[101,2,2,0] vigtd[101,2,2,1]
 betat[0] betat[1] betat[2] betat[3] entryig[101,1] entryig[101,2]
 muig[101,1] muig[101,2]
End
