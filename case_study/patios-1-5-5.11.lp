\ Model PD-Stages
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  dRLt[0] + dRLt[1] + dRLt[2] + dLRt[0] + dLRt[1] + dLRt[2] + dLRt[3]
   + 0 deltat[0] + 0 deltat[1] + 0 deltat[2] + 0 deltat[3] + 0 zetat[0]
   + 0 zetat[1] + 0 zetat[2] + 0 zetat[3]
Subject To
 R0: uigtd[101,1,1,0] + uigtd[101,2,1,0] <= 1
 R1: uigtd[101,1,2,0] + uigtd[101,2,2,0] <= 1
 R2: vigtd[101,1,1,0] + vigtd[101,2,1,0] <= 1
 R3: vigtd[101,1,2,0] + vigtd[101,2,2,0] <= 1
 R4: uigtd[101,1,1,0] + uigtd[101,1,2,0] = 1
 R5: uigtd[101,2,1,0] + uigtd[101,2,2,0] = 1
 R6: vigtd[101,1,1,0] + vigtd[101,1,2,0] = 1
 R7: vigtd[101,2,1,0] + vigtd[101,2,2,0] = 1
 R8: betat[1] - betat[2] <= 0
 R9: betat[2] - betat[3] <= 0
 R10: - 2 betat[1] >= 0
 R11: uigtd[101,1,1,0] + uigtd[101,2,1,0] - 2 betat[2] >= 0
 R12: betat[0] >= 1
 R13: uigtd[101,1,1,0] + uigtd[101,2,1,0] + betat[1] >= 1
 R14: uigtd[101,1,2,0] + uigtd[101,2,2,0] + betat[2] >= 1
 R15: betat[3] >= 1
 R16: - uigtd[101,1,1,0] - uigtd[101,1,2,0] + muig[101,1] = 0
 R17: - uigtd[101,2,1,0] - uigtd[101,2,2,0] + muig[101,2] = 0
 R18: - vigtd[101,1,1,0] - vigtd[101,1,2,0] + muig[101,1] = 0
 R19: - vigtd[101,2,1,0] - vigtd[101,2,2,0] + muig[101,2] = 0
 R20: uigtd[101,1,1,0] - vigtd[101,1,1,0] = 0
 R21: uigtd[101,2,1,0] - vigtd[101,2,1,0] = 0
 R22: uigtd[101,1,2,0] - vigtd[101,1,2,0] = 0
 R23: uigtd[101,2,2,0] - vigtd[101,2,2,0] = 0
 R24: - muig[101,1] + pig[101,1] - alphaig[101,1] >= -1
 R25: - muig[101,2] + pig[101,2] - alphaig[101,2] >= -1
 R26: - muig[101,1] + pig[101,1] <= 0
 R27: - muig[101,2] + pig[101,2] <= 0
 R28: pig[101,1] - alphaig[101,1] <= 0
 R29: pig[101,2] - alphaig[101,2] <= 0
 R30: sig[101,1] >= 0
 R31: sig[101,1] <= 0
 R32: sig[101,2] >= 0
 R33: sig[101,2] <= 0
 R34: difLigtd[101,1,1,0,0] - xLt[1,0] + Rig[101,1,0] >= 0
 R35: difLigtd[101,1,1,0,1] - xLt[1,1] + Rig[101,1,1] >= 0
 R36: difLigtd[101,1,2,0,0] - xLt[2,0] + Rig[101,1,0] >= 0
 R37: difLigtd[101,1,2,0,1] - xLt[2,1] + Rig[101,1,1] >= 0
 R38: difLigtd[101,2,1,0,0] - xLt[1,0] + Rig[101,2,0] >= 0
 R39: difLigtd[101,2,1,0,1] - xLt[1,1] + Rig[101,2,1] >= 0
 R40: difLigtd[101,2,2,0,0] - xLt[2,0] + Rig[101,2,0] >= 0
 R41: difLigtd[101,2,2,0,1] - xLt[2,1] + Rig[101,2,1] >= 0
 R42: difLigtd[101,1,1,0,0] + xLt[1,0] - Rig[101,1,0] >= 0
 R43: difLigtd[101,1,1,0,1] + xLt[1,1] - Rig[101,1,1] >= 0
 R44: difLigtd[101,1,2,0,0] + xLt[2,0] - Rig[101,1,0] >= 0
 R45: difLigtd[101,1,2,0,1] + xLt[2,1] - Rig[101,1,1] >= 0
 R46: difLigtd[101,2,1,0,0] + xLt[1,0] - Rig[101,2,0] >= 0
 R47: difLigtd[101,2,1,0,1] + xLt[1,1] - Rig[101,2,1] >= 0
 R48: difLigtd[101,2,2,0,0] + xLt[2,0] - Rig[101,2,0] >= 0
 R49: difLigtd[101,2,2,0,1] + xLt[2,1] - Rig[101,2,1] >= 0
 R50: - 10000 uigtd[101,1,1,0] + pLigtd[101,1,1,0] <= 0
 R51: - 10000 uigtd[101,1,2,0] + pLigtd[101,1,2,0] <= 0
 R52: - 10000 uigtd[101,2,1,0] + pLigtd[101,2,1,0] <= 0
 R53: - 10000 uigtd[101,2,2,0] + pLigtd[101,2,2,0] <= 0
 R54: - dLigtd[101,1,1,0] + pLigtd[101,1,1,0] <= 0
 R55: - dLigtd[101,1,2,0] + pLigtd[101,1,2,0] <= 0
 R56: - dLigtd[101,2,1,0] + pLigtd[101,2,1,0] <= 0
 R57: - dLigtd[101,2,2,0] + pLigtd[101,2,2,0] <= 0
 R58: pLigtd[101,1,1,0] >= 0
 R59: pLigtd[101,1,2,0] >= 0
 R60: pLigtd[101,2,1,0] >= 0
 R61: pLigtd[101,2,2,0] >= 0
 R62: - 10000 uigtd[101,1,1,0] - dLigtd[101,1,1,0] + pLigtd[101,1,1,0]
   >= -10000
 R63: - 10000 uigtd[101,1,2,0] - dLigtd[101,1,2,0] + pLigtd[101,1,2,0]
   >= -10000
 R64: - 10000 uigtd[101,2,1,0] - dLigtd[101,2,1,0] + pLigtd[101,2,1,0]
   >= -10000
 R65: - 10000 uigtd[101,2,2,0] - dLigtd[101,2,2,0] + pLigtd[101,2,2,0]
   >= -10000
 R66: difRigtd[101,1,1,0,0] + xRt[1,0] - Lig[101,1,0] >= 0
 R67: difRigtd[101,1,1,0,1] + xRt[1,1] - Lig[101,1,1] >= 0
 R68: difRigtd[101,1,2,0,0] + xRt[2,0] - Lig[101,1,0] >= 0
 R69: difRigtd[101,1,2,0,1] + xRt[2,1] - Lig[101,1,1] >= 0
 R70: difRigtd[101,2,1,0,0] + xRt[1,0] - Lig[101,2,0] >= 0
 R71: difRigtd[101,2,1,0,1] + xRt[1,1] - Lig[101,2,1] >= 0
 R72: difRigtd[101,2,2,0,0] + xRt[2,0] - Lig[101,2,0] >= 0
 R73: difRigtd[101,2,2,0,1] + xRt[2,1] - Lig[101,2,1] >= 0
 R74: difRigtd[101,1,1,0,0] - xRt[1,0] + Lig[101,1,0] >= 0
 R75: difRigtd[101,1,1,0,1] - xRt[1,1] + Lig[101,1,1] >= 0
 R76: difRigtd[101,1,2,0,0] - xRt[2,0] + Lig[101,1,0] >= 0
 R77: difRigtd[101,1,2,0,1] - xRt[2,1] + Lig[101,1,1] >= 0
 R78: difRigtd[101,2,1,0,0] - xRt[1,0] + Lig[101,2,0] >= 0
 R79: difRigtd[101,2,1,0,1] - xRt[1,1] + Lig[101,2,1] >= 0
 R80: difRigtd[101,2,2,0,0] - xRt[2,0] + Lig[101,2,0] >= 0
 R81: difRigtd[101,2,2,0,1] - xRt[2,1] + Lig[101,2,1] >= 0
 R82: - 10000 vigtd[101,1,1,0] + pRigtd[101,1,1,0] <= 0
 R83: - 10000 vigtd[101,1,2,0] + pRigtd[101,1,2,0] <= 0
 R84: - 10000 vigtd[101,2,1,0] + pRigtd[101,2,1,0] <= 0
 R85: - 10000 vigtd[101,2,2,0] + pRigtd[101,2,2,0] <= 0
 R86: - dRigtd[101,1,1,0] + pRigtd[101,1,1,0] <= 0
 R87: - dRigtd[101,1,2,0] + pRigtd[101,1,2,0] <= 0
 R88: - dRigtd[101,2,1,0] + pRigtd[101,2,1,0] <= 0
 R89: - dRigtd[101,2,2,0] + pRigtd[101,2,2,0] <= 0
 R90: pRigtd[101,1,1,0] >= 0
 R91: pRigtd[101,1,2,0] >= 0
 R92: pRigtd[101,2,1,0] >= 0
 R93: pRigtd[101,2,2,0] >= 0
 R94: - 10000 vigtd[101,1,1,0] - dRigtd[101,1,1,0] + pRigtd[101,1,1,0]
   >= -10000
 R95: - 10000 vigtd[101,1,2,0] - dRigtd[101,1,2,0] + pRigtd[101,1,2,0]
   >= -10000
 R96: - 10000 vigtd[101,2,1,0] - dRigtd[101,2,1,0] + pRigtd[101,2,1,0]
   >= -10000
 R97: - 10000 vigtd[101,2,2,0] - dRigtd[101,2,2,0] + pRigtd[101,2,2,0]
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
 R110: difLRt[0,0] - xLt[0,0] + xRt[0,0] >= 0
 R111: difLRt[0,1] - xLt[0,1] + xRt[0,1] >= 0
 R112: difLRt[1,0] - xLt[1,0] + xRt[1,0] >= 0
 R113: difLRt[1,1] - xLt[1,1] + xRt[1,1] >= 0
 R114: difLRt[2,0] - xLt[2,0] + xRt[2,0] >= 0
 R115: difLRt[2,1] - xLt[2,1] + xRt[2,1] >= 0
 R116: difLRt[3,0] - xLt[3,0] + xRt[3,0] >= 0
 R117: difLRt[3,1] - xLt[3,1] + xRt[3,1] >= 0
 R118: difLRt[0,0] + xLt[0,0] - xRt[0,0] >= 0
 R119: difLRt[0,1] + xLt[0,1] - xRt[0,1] >= 0
 R120: difLRt[1,0] + xLt[1,0] - xRt[1,0] >= 0
 R121: difLRt[1,1] + xLt[1,1] - xRt[1,1] >= 0
 R122: difLRt[2,0] + xLt[2,0] - xRt[2,0] >= 0
 R123: difLRt[2,1] + xLt[2,1] - xRt[2,1] >= 0
 R124: difLRt[3,0] + xLt[3,0] - xRt[3,0] >= 0
 R125: difLRt[3,1] + xLt[3,1] - xRt[3,1] >= 0
 R126: 5 uigtd[101,1,1,0] + 0.1956947162426614 pLigtd[101,1,1,0]
   + 0.1956947162426614 pRigtd[101,1,1,0] - dLRt[1]
   + 1.95695e-06 pig[101,1] <= 5
 R127: 5 uigtd[101,2,1,0] + 0.1956947162426614 pLigtd[101,2,1,0]
   + 0.1956947162426614 pRigtd[101,2,1,0] - dLRt[1]
   + 1.95695e-06 pig[101,2] <= 5
 R128: 5 uigtd[101,1,2,0] + 0.1956947162426614 pLigtd[101,1,2,0]
   + 0.1956947162426614 pRigtd[101,1,2,0] - dLRt[2]
   + 1.95695e-06 pig[101,1] <= 5
 R129: 5 uigtd[101,2,2,0] + 0.1956947162426614 pLigtd[101,2,2,0]
   + 0.1956947162426614 pRigtd[101,2,2,0] - dLRt[2]
   + 1.95695e-06 pig[101,2] <= 5
 R130: dLRt[1] <= 5
 R131: dLRt[2] <= 5
 R132: rhoig[101,1] - landaig[101,1] + minig[101,1] - maxig[101,1] = 0
 R133: minig[101,1] + maxig[101,1] - alphaig[101,1] = 0
 R134: maxig[101,1] + entryig[101,1] <= 1
 R135: minig[101,1] - entryig[101,1] <= 0
 R136: Rig[101,1,0] = 11
 R137: Rig[101,1,1] + 1e-05 rhoig[101,1] = 20.00001
 R138: Lig[101,1,0] = 11
 R139: Lig[101,1,1] + 1e-05 landaig[101,1] = 20.00001
 R140: rhoig[101,2] - landaig[101,2] + minig[101,2] - maxig[101,2] = 0
 R141: minig[101,2] + maxig[101,2] - alphaig[101,2] = 0
 R142: maxig[101,2] + entryig[101,2] <= 1
 R143: minig[101,2] - entryig[101,2] <= 0
 R144: Rig[101,2,0] = 13
 R145: Rig[101,2,1] + 1e-05 rhoig[101,2] = 20.00001
 R146: Lig[101,2,0] = 13
 R147: Lig[101,2,1] + 1e-05 landaig[101,2] = 20.00001
 R148: 1e-05 pig[101,1] = 1e-11
 R149: 1e-05 pig[101,2] = 1e-11
 R150: xLt[0,0] = 0
 R151: xLt[0,1] = 5
 R152: xRt[0,0] = 0
 R153: xRt[0,1] = 5
 R154: xLt[3,0] = 20
 R155: xLt[3,1] = 5
 R156: xRt[3,0] = 20
 R157: xRt[3,1] = 5
 difLigtd[101,1,1,0]: [ - dLigtd[101,1,1,0] ^2 + difLigtd[101,1,1,0,0] ^2
   + difLigtd[101,1,1,0,1] ^2 ] <= 0
 difLigtd[101,1,2,0]: [ - dLigtd[101,1,2,0] ^2 + difLigtd[101,1,2,0,0] ^2
   + difLigtd[101,1,2,0,1] ^2 ] <= 0
 difLigtd[101,2,1,0]: [ - dLigtd[101,2,1,0] ^2 + difLigtd[101,2,1,0,0] ^2
   + difLigtd[101,2,1,0,1] ^2 ] <= 0
 difLigtd[101,2,2,0]: [ - dLigtd[101,2,2,0] ^2 + difLigtd[101,2,2,0,0] ^2
   + difLigtd[101,2,2,0,1] ^2 ] <= 0
 difRigtd[101,1,1,0]: [ - dRigtd[101,1,1,0] ^2 + difRigtd[101,1,1,0,0] ^2
   + difRigtd[101,1,1,0,1] ^2 ] <= 0
 difRigtd[101,1,2,0]: [ - dRigtd[101,1,2,0] ^2 + difRigtd[101,1,2,0,0] ^2
   + difRigtd[101,1,2,0,1] ^2 ] <= 0
 difRigtd[101,2,1,0]: [ - dRigtd[101,2,1,0] ^2 + difRigtd[101,2,1,0,0] ^2
   + difRigtd[101,2,1,0,1] ^2 ] <= 0
 difRigtd[101,2,2,0]: [ - dRigtd[101,2,2,0] ^2 + difRigtd[101,2,2,0,0] ^2
   + difRigtd[101,2,2,0,1] ^2 ] <= 0
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
 uigtd[101,1,1,0] uigtd[101,1,2,0] uigtd[101,2,1,0] uigtd[101,2,2,0]
 vigtd[101,1,1,0] vigtd[101,1,2,0] vigtd[101,2,1,0] vigtd[101,2,2,0]
 betat[0] betat[1] betat[2] betat[3] entryig[101,1] entryig[101,2]
 muig[101,1] muig[101,2]
End
