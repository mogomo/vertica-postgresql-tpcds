# Answers: 20261031-0054_sf1_vertica_smoke (a) vs 20261031-0106_sf1_postgresql_smoke (b)

different: 10, same: 85, same rows: 4

| Query | Rows a | Rows b | Result |
|---:|---:|---:|---|
| 1 | 100 | 100 | same |
| 2 | 2513 | 2513 | same |
| 3 | 38 | 38 | same |
| 4 | 8 | 0 | different (8 rows only in a, 0 only in b) |
| 5 | 100 | 100 | same |
| 6 | 41 | 41 | same |
| 7 | 100 | 100 | same |
| 8 | 0 | 0 | same |
| 9 | 1 | 1 | same |
| 10 | 2 | 2 | same |
| 11 | 88 | 0 | different (88 rows only in a, 0 only in b) |
| 12 | 100 | 100 | same |
| 13 | 1 | 1 | same |
| 14 | 200 | 200 | different (2 rows only in a, 2 only in b) |
| 15 | 100 | 100 | same |
| 16 | 1 | 1 | same |
| 17 | 1 | 1 | different (1 rows only in a, 1 only in b) |
| 18 | 100 | 100 | same |
| 19 | 100 | 100 | same |
| 20 | 100 | 100 | same |
| 21 | 100 | 100 | different (43 rows only in a, 43 only in b) |
| 22 | 100 | 100 | same |
| 23 | 1 | 1 | same |
| 24 | 0 | 0 | same |
| 25 | 0 | 0 | same |
| 26 | 100 | 100 | same |
| 27 | 100 | 100 | same |
| 28 | 1 | 1 | same |
| 29 | 0 | 0 | same |
| 30 | 92 | 92 | same |
| 31 | 51 | 51 | same rows |
| 32 | 1 | 1 | same |
| 33 | 100 | 100 | same |
| 34 | 451 | 347 | different (104 rows only in a, 0 only in b) |
| 35 | 100 | 100 | same |
| 36 | 100 | 100 | same |
| 37 | 0 | 0 | same |
| 38 | 1 | 1 | same |
| 39 | 153 | 153 | same |
| 40 | 100 | 100 | same |
| 41 | 0 | 0 | same |
| 42 | 10 | 10 | same |
| 43 | 6 | 6 | same |
| 44 | 10 | 10 | same |
| 45 | 16 | 16 | same |
| 46 | 100 | 100 | same |
| 47 | 100 | 100 | same |
| 48 | 1 | 1 | same |
| 49 | 31 | 31 | same |
| 50 | 6 | 6 | same |
| 51 | 100 | 100 | same |
| 52 | 100 | 100 | same |
| 53 | 14 | 14 | same |
| 54 | 0 | 0 | same |
| 55 | 69 | 69 | same |
| 56 | 78 | 78 | same |
| 57 | 100 | 100 | same |
| 58 | 0 | 0 | same |
| 59 | 100 | 100 | same |
| 60 | 100 | 100 | same |
| 61 | 1 | 1 | same |
| 62 | 100 | 100 | same |
| 63 | 44 | 44 | same |
| 64 | 10 | 10 | same |
| 65 | 100 | 100 | same |
| 66 | 5 | 5 | same |
| 67 | 100 | 100 | same |
| 68 | 100 | 100 | same |
| 69 | 100 | 100 | same |
| 70 | 3 | 3 | same |
| 71 | 1102 | 1102 | same rows |
| 72 | 100 | 100 | same |
| 73 | 9 | 5 | different (4 rows only in a, 0 only in b) |
| 74 | 90 | 90 | same |
| 75 | 100 | 100 | same |
| 76 | 100 | 100 | same |
| 77 | 44 | 44 | same rows |
| 78 | 100 | 100 | different (92 rows only in a, 92 only in b) |
| 79 | 100 | 100 | same rows |
| 80 | 100 | 100 | same |
| 81 | 96 | 96 | same |
| 82 | 1 | 1 | same |
| 83 | 4 | 4 | different (4 rows only in a, 4 only in b) |
| 84 | 22 | 22 | same |
| 85 | 3 | 3 | same |
| 86 | 100 | 100 | same |
| 87 | 1 | 1 | same |
| 88 | 1 | 1 | same |
| 89 | 100 | 100 | same |
| 90 | 1 | 1 | same |
| 91 | 4 | 4 | same |
| 92 | 1 | 1 | same |
| 93 | 100 | 100 | different (100 rows only in a, 100 only in b) |
| 94 | 1 | 1 | same |
| 95 | 1 | 1 | same |
| 96 | 1 | 1 | same |
| 97 | 1 | 1 | same |
| 98 | 2486 | 2486 | same |
| 99 | 90 | 90 | same |

## Query 4

Only in a (first 5):
```
AAAAAAAABIJBAAAA|James|White|James.White@DI8oHLVIxJer5MMljj.org
AAAAAAAADIIOAAAA|David|Carroll|David.Carroll@fm.edu
AAAAAAAAIJCIBAAA|Thomas|Oneal|Thomas.Oneal@YhHzOk6o3RiKc1AREv.edu
AAAAAAAAKJBLAAAA|Kerry|Davis|Kerry.Davis@i.com
AAAAAAAAMFPFBAAA|Jamie|Woods|Jamie.Woods@zjTJlz.edu
```
Only in b (first 5):
```
```

## Query 11

Only in a (first 5):
```
AAAAAAAAAFGBBAAA|Howard|Major|Howard.Major@vTgpJKpgAR5.com
AAAAAAAAAMGDAAAA|Kenneth|Harlan|Kenneth.Harlan@HlOPitjATDz.com
AAAAAAAAAOPFBAAA|Jerry|Fields|Jerry.Fields@Ojv.com
AAAAAAAABLEIBAAA|Paula|Wakefield|Paula.Wakefield@MguENzr.org
AAAAAAAABNBBAAAA|Irma|Smith|Irma.Smith@dOdDOArM.com
```
Only in b (first 5):
```
```

## Query 14

Only in a (first 5):
```
catalog||||2.3662e+08|46416
catalog|1.002e+06|||2.99308e+06|599
```
Only in b (first 5):
```
catalog|1.002e+06|5|1|77373.7|10
catalog|1.002e+06|6|1|18386.9|7
```

## Query 17

Only in a (first 5):
```
AAAAAAAANCBAAAAA|As eastern pupils help new resources. Radical weeks should enable over circumstances; casual characteristics ought to manage yet anima|TN|1|56|nan|nan|1|8|nan|nan|1|12|nan|nan
```
Only in b (first 5):
```
AAAAAAAANCBAAAAA|As eastern pupils help new resources. Radical weeks should enable over circumstances; casual characteristics ought to manage yet anima|TN|1|56|||1|8|||1|12||
```

## Query 21

Only in a (first 5):
```
Bad cards must make.|AAAAAAAAAALAAAAA|1730|1683
Bad cards must make.|AAAAAAAAABBDAAAA|2174|1651
Bad cards must make.|AAAAAAAAABDAAAAA|1515|1151
Bad cards must make.|AAAAAAAAACHCAAAA|1748|1535
Bad cards must make.|AAAAAAAAACKCAAAA|1912|1281
```
Only in b (first 5):
```
Bad cards must make.|AAAAAAAAACLDAAAA|1692|2677
Bad cards must make.|AAAAAAAAADKBAAAA|1666|2569
Bad cards must make.|AAAAAAAAAHHAAAAA|1374|2258
Bad cards must make.|AAAAAAAAAJACAAAA|1047|1990
Bad cards must make.|AAAAAAAAAJEDAAAA|1188|2232
```

## Query 34

Only in a (first 5):
```
Abbott|Harriet|Ms.|N|195008|15
Acuna|Ronald|Dr.|N|119381|15
Alba|Rosemary|Miss|Y|197139|16
Anderson|Martha|Mrs.|N|74295|15
Ashton|Irma|Mrs.|Y|99233|15
```
Only in b (first 5):
```
```

## Query 73

Only in a (first 5):
```
Graham|Josette|Ms.|Y|92639|5
Peterson|Chantell|Miss|N|47551|5
Steadman|Trinidad|Dr.|N|139138|5
Woodbury|Michael|Sir|Y|86207|5
```
Only in b (first 5):
```
```

## Query 78

Only in a (first 5):
```
2000|116|51507|8.91|98|45.86|80.12|11|46.07|39.52
2000|119|51419|0.81|60|52.03|86.53|74|68.27|31.33
2000|277|52580|1.92|23|44.62|13.73|12|4.43|5.98
2000|386|37347|3.64|91|43.97|62.43|25|49.56|54.63
2000|415|6082|1.4|21|10.69|9.28|15|84.25|151.18
```
Only in b (first 5):
```
2000|116|51507|8|98|45.86|80.12|11|46.07|39.52
2000|119|51419|0|60|52.03|86.53|74|68.27|31.33
2000|277|52580|1|23|44.62|13.73|12|4.43|5.98
2000|386|37347|3|91|43.97|62.43|25|49.56|54.63
2000|415|6082|1|21|10.69|9.28|15|84.25|151.18
```

## Query 83

Only in a (first 5):
```
AAAAAAAAAHKAAAAA|24|11.2676|39|18.3099|8|3.75587|23.6667
AAAAAAAAIFNDAAAA|4|1.8018|10|4.5045|60|27.027|24.6667
AAAAAAAAKJADAAAA|17|8.09524|51|24.2857|2|0.952381|23.3333
AAAAAAAAOAIBAAAA|40|13.6054|32|10.8844|26|8.84354|32.6667
```
Only in b (first 5):
```
AAAAAAAAAHKAAAAA|24|0|39|0|8|0|23.6667
AAAAAAAAIFNDAAAA|4|0|10|0|60|0|24.6667
AAAAAAAAKJADAAAA|17|0|51|0|2|0|23.3333
AAAAAAAAOAIBAAAA|40|0|32|0|26|0|32.6667
```

## Query 93

Only in a (first 5):
```
16|
66|
431|
442|
857|
```
Only in b (first 5):
```
126|0
169|0
197|0
300|0
540|0
```
