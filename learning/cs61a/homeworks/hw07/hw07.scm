(define (square n) (* n n))

(define (pow base exp)
  (cond ((zero? exp) 1)
        ((= (modulo exp 2) 1)
          (* base (pow base (- exp 1)))
        )
        ((zero? (modulo exp 2))
          (square (pow base (quotient exp 2)))
        )
  )
)

(define (repeatedly-cube n x)
  (if (zero? n)
      x
      (begin (define y (lambda (s) (* s s s)))
             (y (repeatedly-cube (- n 1) x))
      )
  )
)

(define (cddr s) (cdr (cdr s)))

(define (cadr s)
  (car (cdr s))
)

(define (caddr s)
  (car (cddr s))
)
