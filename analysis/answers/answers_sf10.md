# Answers: 20261031-0132_sf10_vertica_tuned (a) vs 20261031-0145_sf10_postgresql_tuned (b)

different: 11, same: 83, same rows: 5

| Query | Rows a | Rows b | Result |
|---:|---:|---:|---|
| 1 | 100 | 0 | different (100 rows only in a, 0 only in b) |
| 2 | 2513 | 2513 | same |
| 3 | 100 | 100 | same |
| 4 | 100 | 0 | different (100 rows only in a, 0 only in b) |
| 5 | 100 | 100 | same |
| 6 | 51 | 0 | different (51 rows only in a, 0 only in b) |
| 7 | 100 | 100 | same |
| 8 | 8 | 8 | same |
| 9 | 1 | 1 | same |
| 10 | 100 | 100 | same |
| 11 | 100 | 0 | different (100 rows only in a, 0 only in b) |
| 12 | 100 | 100 | same |
| 13 | 1 | 1 | same |
| 14 | 200 | 0 | different (200 rows only in a, 0 only in b) |
| 15 | 100 | 100 | same |
| 16 | 1 | 1 | same |
| 17 | 3 | 3 | different (3 rows only in a, 3 only in b) |
| 18 | 100 | 100 | same |
| 19 | 100 | 100 | same |
| 20 | 100 | 100 | same |
| 21 | 100 | 100 | same |
| 22 | 100 | 100 | same |
| 23 | 2 | 2 | same |
| 24 | 1 | 1 | same |
| 25 | 4 | 4 | same |
| 26 | 100 | 100 | same |
| 27 | 100 | 100 | same |
| 28 | 1 | 1 | same |
| 29 | 3 | 3 | same |
| 30 | 100 | 0 | different (100 rows only in a, 0 only in b) |
| 31 | 288 | 288 | same rows |
| 32 | 1 | 1 | same |
| 33 | 100 | 100 | same |
| 34 | 4569 | 4569 | same |
| 35 | 100 | 100 | same |
| 36 | 100 | 100 | same |
| 37 | 3 | 3 | same |
| 38 | 1 | 1 | same |
| 39 | 1715 | 1715 | same |
| 40 | 100 | 100 | same |
| 41 | 42 | 42 | same |
| 42 | 11 | 11 | same |
| 43 | 17 | 17 | same |
| 44 | 0 | 0 | same |
| 45 | 36 | 36 | same |
| 46 | 100 | 100 | same |
| 47 | 100 | 100 | same |
| 48 | 1 | 1 | same |
| 49 | 45 | 45 | same |
| 50 | 51 | 51 | same rows |
| 51 | 100 | 100 | same |
| 52 | 100 | 100 | same |
| 53 | 100 | 100 | same |
| 54 | 0 | 0 | same |
| 55 | 100 | 100 | same |
| 56 | 100 | 100 | same |
| 57 | 100 | 100 | same |
| 58 | 5 | 5 | same |
| 59 | 100 | 100 | same |
| 60 | 100 | 100 | same |
| 61 | 1 | 1 | same |
| 62 | 100 | 100 | same |
| 63 | 100 | 100 | same |
| 64 | 20 | 20 | same |
| 65 | 100 | 100 | same rows |
| 66 | 10 | 10 | same |
| 67 | 100 | 100 | same |
| 68 | 100 | 100 | same |
| 69 | 100 | 100 | same |
| 70 | 8 | 8 | same |
| 71 | 10477 | 10477 | same rows |
| 72 | 100 | 100 | same |
| 73 | 43 | 43 | same rows |
| 74 | 100 | 0 | different (100 rows only in a, 0 only in b) |
| 75 | 100 | 100 | same |
| 76 | 100 | 100 | same |
| 77 | 100 | 100 | different (1 rows only in a, 1 only in b) |
| 78 | 100 | 100 | same |
| 79 | 100 | 100 | same |
| 80 | 100 | 100 | same |
| 81 | 100 | 0 | different (100 rows only in a, 0 only in b) |
| 82 | 10 | 10 | same |
| 83 | 100 | 100 | same |
| 84 | 100 | 100 | same |
| 85 | 14 | 14 | same |
| 86 | 100 | 100 | same |
| 87 | 1 | 1 | same |
| 88 | 1 | 1 | same |
| 89 | 100 | 100 | same |
| 90 | 1 | 1 | same |
| 91 | 13 | 13 | same |
| 92 | 1 | 1 | same |
| 93 | 100 | 100 | different (100 rows only in a, 100 only in b) |
| 94 | 1 | 1 | same |
| 95 | 1 | 1 | same |
| 96 | 1 | 1 | same |
| 97 | 1 | 1 | same |
| 98 | 15070 | 15070 | same |
| 99 | 100 | 100 | same |

## Query 1

Only in a (first 5):
```
AAAAAAAAAAABEAAA
AAAAAAAAAAACDAAA
AAAAAAAAAAAEEAAA
AAAAAAAAAAAEFAAA
AAAAAAAAAAAEHAAA
```
Only in b (first 5):
```
```

## Query 4

Only in a (first 5):
```
AAAAAAAAAAEFEAAA|Wayne|Coble|Wayne.Coble@YgcTMHB9aVjF.edu
AAAAAAAAABCJDAAA||Cortez|James.Cortez@899DCEthMB53yNB.edu
AAAAAAAAABIBHAAA|Gloria|Thurman|Gloria.Thurman@IVKXBKpT77LA9.edu
AAAAAAAAACGNEAAA|William|Miller|William.Miller@7MGRbM.com
AAAAAAAAACKHDAAA|Waltraud|Brannon|Waltraud.Brannon@jcVx.org
```
Only in b (first 5):
```
```

## Query 6

Only in a (first 5):
```
RI|14
DE|25
HI|28
CT|55
NH|64
```
Only in b (first 5):
```
```

## Query 11

Only in a (first 5):
```
AAAAAAAAAABECAAA|Sharon|Thompson|Sharon.Thompson@jkE.edu
AAAAAAAAAACCEAAA|Delphia|Hall|Delphia.Hall@LZb.com
AAAAAAAAAACGAAAA|Elizabeth|Martin|Elizabeth.Martin@p2MsdEgAM7.com
AAAAAAAAAADMAAAA|Linda|Fuller|Linda.Fuller@74cRU7hjaf.org
AAAAAAAAAAEDDAAA|Randall|Hall|Randall.Hall@Z.edu
```
Only in b (first 5):
```
```

## Query 14

Only in a (first 5):
```
catalog||||2.37779e+09|467664
catalog|1.001e+06|||2.90256e+07|5771
catalog|1.001e+06|1||2.49153e+07|4909
catalog|1.001e+06|1|1|1.99908e+07|3943
catalog|1.001e+06|1|2|365065|73
```
Only in b (first 5):
```
```

## Query 17

Only in a (first 5):
```
AAAAAAAAHFHGAAAA|Chinese, optimistic men allow in common possible, political cells; vital, major offices could make also. Nice, burning clients may make major, normal years. Legisla|AL|1|24|nan|nan|1|6|nan|nan|1|92|nan|nan
AAAAAAAAKBGFAAAA|International developments blame rights. Complete effects might join members. Areas ought to touch. In addition excellent strengths used to move books. Vulnerable pr|TN|0||||1|67|nan|nan|1|16|nan|nan
AAAAAAAANHOMAAAA|Costly|AL|1|52|nan|nan|1|8|nan|nan|1|5|nan|nan
```
Only in b (first 5):
```
AAAAAAAAHFHGAAAA|Chinese, optimistic men allow in common possible, political cells; vital, major offices could make also. Nice, burning clients may make major, normal years. Legisla|AL|1|24|||1|6|||1|92||
AAAAAAAAKBGFAAAA|International developments blame rights. Complete effects might join members. Areas ought to touch. In addition excellent strengths used to move books. Vulnerable pr|TN|0||||1|67|||1|16||
AAAAAAAANHOMAAAA|Costly|AL|1|52|||1|8|||1|5||
```

## Query 30

Only in a (first 5):
```
AAAAAAAAAAECEAAA|Miss|Mildred|Johnson|Y|7|2|1988|BERMUDA||Mildred.Johnson@sbadT8dhzP0a.edu|2.45239e+06|2793.18
AAAAAAAAAAEKDAAA|Dr.|Roy|Ortiz|N|4|1|1978|ANGOLA||Roy.Ortiz@N5r4.org|2.45235e+06|4459.66
AAAAAAAAAALEDAAA|Dr.|Charles|Carter|Y|7|1|1940|ZIMBABWE||Charles.Carter@6Sg6EiN4gsO.com|2.45261e+06|4713.3
AAAAAAAAAAMPFAAA|Dr.|George|Yount|Y|9|5|1978|NETHERLANDS ANTILLES||George.Yount@YApjfBkz2.edu|2.45263e+06|2341.53
AAAAAAAAAAPKFAAA|Mr.|Richard|Buford|Y|24|6|1979|AMERICAN SAMOA||Richard.Buford@xzUBDHcNun0PVfyCeQ.org|2.45237e+06|4257.24
```
Only in b (first 5):
```
```

## Query 74

Only in a (first 5):
```
AAAAAAAACFCEDAAA|Aaron|Lai
AAAAAAAACMEAFAAA|Aaron|Dixon
AAAAAAAADBGKEAAA|Aaron|Green
AAAAAAAADDJKEAAA|Aaron|Long
AAAAAAAALDPFGAAA|Aaron|Johnson
```
Only in b (first 5):
```
```

## Query 77

Only in a (first 5):
```
web channel||4.07797e+08|6.08076e+06|-4.41233e+07
```
Only in b (first 5):
```
web channel|67|4.24726e+06|42908.5|-283088
```

## Query 81

Only in a (first 5):
```
AAAAAAAAAAJICAAA|Dr.|Owen|Davis|472|2nd Hickory|Cir.|Suite E|Clinton|Fulton County|IL|68222|United States|-6|single family|8247.93
AAAAAAAAAALDBAAA|Sir|Mickey|Keaton|754|Church Mill|Ave|Suite 260|Mount Pleasant|Will County|IL|61933|United States|-6|apartment|3000.03
AAAAAAAAABDGEAAA||Ashley|Sanders|789|West Jackson|Court|Suite 150|Summit|Clark County|IL|60499|United States|-6|condo|4043.84
AAAAAAAAABINEAAA|Mrs.|Evelyn|Cuellar|794|13th|Wy|Suite E|Green Acres|Edgar County|IL|67683|United States|-6|single family|3857.8
AAAAAAAAABMAHAAA|Dr.|Marcia|White|266|Walnut|Boulevard|Suite 460|Deerfield|Kendall County|IL|69840|United States|-6|condo|3785.94
```
Only in b (first 5):
```
```

## Query 93

Only in a (first 5):
```
20|
27|
404|
463|
553|
```
Only in b (first 5):
```
76|0
308|0
371|0
619|0
852|0
```
