(define (over-or-under num1 num2)
  (cond ((< num1 num2) -1)
        ((> num1 num2) 1)
        (else 0)))

(define (make-adder num)
  (lambda (inc) (+ num inc))
)

(define (composed f g)
  (lambda (arg) (f (g arg)))
)

(define (repeat f n)
  (cond ((> n 1) (composed f (repeat f (- n 1))))
        (else f)
  )
)

(define (max a b)
  (if (> a b)
      a
      b))

(define (min a b)
  (if (> a b)
      b
      a))

(define (gcd a b)
  (cond ((> (min a b) 1) (gcd (min a b) (modulo (max a b) (min a b))))
        (else (max a b))
  )
)
