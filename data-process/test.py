from matching import impute_list

a = [1, 2, 0, 4]
print a
impute_list(a, 0)
print a
print "--------------"
a = [1, 2, 0, 0]
print a
impute_list(a, 0)
print a
print "--------------"
a = [1, 2, 0, 0, 5]
print a
impute_list(a, 0)
print a
print "--------------"
a = [0, 0, 0, 1]
print a
impute_list(a, 0)
print a
print "--------------"
a = [0, 0, 0, 0]
print a
impute_list(a, 0)
print a
print "--------------"
a = [0.0, 0.0, 0.0, 1.0,3.0,2.0,0.0,0.0,0.0,8.0,10.0,0.0]
print a
impute_list(a, 0)
print a
print "--------------"
a = [0.0, 0.0, 0.0, 1.0,3.0,2.0,0.0,0.0,0.0,8.0,0.0,0.0,10.0,0.0]
print a
impute_list(a, 0)
print a
print "--------------"