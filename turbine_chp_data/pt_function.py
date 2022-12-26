



def getNt(Qt, Qp, pt, pn):
  return 0.529 * Qt * pow(0.12 / pt, 0.14) + 0.305 * Qp * pow(1.3/pn, 0.34) - (9.9 - 0.048 * Qt)


pt = 0.1176
pn = 1.274

 

Qp = 228
Qt = 0

Nt = getNt(0, Qp, pt, pn)
HR_P = 16.3 + 2.33*Nt - 1.314 * Nt  + Qt + Qp

print("макс. П расход = ", HR_P, 'при нагрузке П-отбора = ', Qp,'соотношение', Qp/60)




Qt = 121
Qp = 0
Nt = getNt(Qt, 0, pt, pn)
HR_T = 16.3 + 2.33 * Nt - 1.314 * Nt  + Qt + Qp

print("макс. Т расход = ", HR_T, 'при нагрузке Т-отбора = ', Qt,'соотношение', Qt/60)



Qc = 198.3598


