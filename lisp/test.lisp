(defun double (x) (* x 2))

(print (double 10))

(defmacro mac (exp1 exp2) `(,exp1 (,exp1 ,exp2)))

(print (mac double 10))
