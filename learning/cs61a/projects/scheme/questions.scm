(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cadar x) (car (cdr (car x))))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

;; Problem 13
;; Returns a list of two-element lists
(define (enumerate s)
  ; BEGIN PROBLEM 13
  (begin
    (define (enum i lst)
      (if(null? lst)
        nil
        (cons (list i (car lst)) (enum (+ i 1) (cdr lst)))
      )
    )
    (enum 0 s)
  )
  ; END PROBLEM 13
)


;; Problem 14

;; Return the value for a key in a dictionary list
(define (get dict key)
  ; BEGIN PROBLEM 14
  (begin
  (if (null? dict)
    #f
    (if (equal? key (caar dict))
      (cadar dict)
      (get (cdr dict) key)
    )
  )
  )
  ; END PROBLEM 14
)

;; Return a dictionary list with a (key value) pair
(define (set dict key val)
  ; BEGIN PROBLEM 14
  (begin
    (if (null? dict)
      (cons (list key val) nil)
      (if (equal? key (caar dict))
        (cons (list key val) (cdr dict))
        (cons (car dict) (set (cdr dict) key val))
      )
    )
  )
  ; END PROBLEM 14
)

;; Problem 15

;; implement solution-code
(define (solution-code problem solution)
  ; BEGIN PROBLEM 15
  (begin
    (if (null? problem)
      nil
      (if (list? problem)
        (begin
          (if (equal? (car problem) '_____)
            (cons
              solution
              (solution-code (cdr problem) solution)
            )
            (cons
              (solution-code (car problem) solution)
              (solution-code (cdr problem) solution)
            )
          )
        )
        problem
      )
    )
  )
  ; END PROBLEM 15
)
