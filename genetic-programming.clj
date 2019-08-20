(ns genifer6.GeneticAlgorithm
  (:require [genifer6.toClara :refer :all]))

; TO-DO:
; * Beware especially of synergistic interactions

; STANDARD EVOLUTIONARY ALGORITHM
; ===============================
; Initialize population
; Repeat until success:
;    Select parents
;    Recombine, mutate
;    Evaluate
;    Select survivors

; STRUCTURE OF THE GENOME
; =======================
; * The genome is a set of rules, which evolve co-operatively.
; * Each candidate = just one rule.
; * Each rule = [ head => tail ]
; * Heads and tails are composed from "var" symbols and "const" symbols.
; * Rules have variable length, OK?
;   -- as long as their lengths can decrease during learning

; SCORING OF RULES
; ================
; * For each generation, rules should be allowed to fire plentifully
; * Some facts lead to rewards
; * The chains of inference can be inspected in Clara Rules

; STRUCTURE OF A RULE
; ===================
;    [ [] [] ] => []
; =  pair( list of lists , list )

; Logic parameters:
(def numPreds (atom 10))
(def numVars (atom 4))
(def numConsts (atom 30))
(def const2varRatio 0.6)       ; 0.6 means 60% consts
(def const2varFlipRate 0.5)    ; probability of "var <--> const"

; Evolution parameters:
(def maxGens 100)
(def popSize 100)
(def crossRate 0.98)
(def mutationRate (/ 1.0 10))

(defn fitness [gene]
  0)

; Print a proposition
(defn printProp [prop]
  (doseq [term prop]
    (print term)))

(defn printRule [rule]
  (print "〈" (fitness rule) "〉")
  (def isFirst (atom true))
  (doseq [prop (first rule)]
    (if (not @isFirst)
      (print " ∧ "))
    (reset! isFirst nil)
    (printProp prop))
  (print " → ")
  (printProp (second rule))
  (println))

(defn randomPred []
  (keyword (str "p" (rand-int @numPreds))))

(defn randomTerm []
  (keyword
    (if (> (rand) const2varRatio)
      (str "v" (rand-int @numVars))
      (str "c" (rand-int @numConsts)))))

; Generate a random proposition
; Format: [ predicate term1 term2 ... ]
; where "term" can be "var" or "const"
(defn randomProp []
  (cons
    (randomPred)
    (take (rand-int 4) (repeatedly
      #(randomTerm)))))

; Generate a random rule
; Format: [ [] [] ] => []
(defn randomRule []
  (vector
    (take (rand-int 4) (repeatedly
      #(randomProp)))
    (randomProp)))

(def randomGene randomRule)   ; Just an alias

(defn ruleLength [rule]
  (+
    (reduce +
      (for [prop (first rule)]
        (count prop)))
    (count (second rule))))

; Pick 2 random candidates, select the one with higher fitness
; This step would be repeated for the entire population.
(defn binaryTournament [pop]
  (let [i (rand-int popSize)
        j (rand-int popSize)
        x (nth pop i)
        y (nth pop j)]
    (if (> (fitness x) (fitness y))
      x
      y)))

; The following changes are possible:
; * var --> const
; * var / const --> different var / const
; * pred --> different pred
(defn mutateTerm [term]
  (case (first (name term))
    \p (keyword (str \p (rand-int @numPreds)))
    \v (if (> (rand) const2varFlipRate)
          (keyword (str \v (rand-int @numVars)))
          (keyword (str \c (rand-int @numConsts))))
    \c (if (> (rand) const2varFlipRate)
          (keyword (str \c (rand-int @numConsts)))
          (keyword (str \v (rand-int @numVars))))))

; Mutate one proposition (= list of terms)
; rate = mutation rate at each term
(defn mutateProp [prop rate]
    (map (fn [x] (if (> (rand) rate)
            x
            (mutateTerm x)))
      prop))

; Randomly mutate a rule.
; Rule's length = # of times to attempt mutation.
; rate = 1/(rule's length), so longer rule, lower mutation rate
(defn mutateRule [rule & [mutation-rate]]
  (let [rate (if mutation-rate
        mutation-rate
        (/ 1.0 (ruleLength rule)))]

    (vector
      (for [prop (first rule)]
        (mutateProp prop rate))
      (mutateProp (second rule) rate))))

(def pointMutate mutateRule)    ; alias

; Pick a point within Parent1,
; cross Parent1's gene with Parent2's
(defn crossover [parent1 parent2 crossover-rate]
  (if (> (rand) crossover-rate)
    parent1

    (let [i (rand-int (+ 1 64))]
      (concat (take i parent1) (drop i parent2)))))

  ; println("p1: " + parent1)
  ; println("mx: " + mix)
  ; println("p2: " + parent2)
  ; print  ("  : ")
  ; for (i <- 0 until point)
  ;  print(" ")
  ; println("^\n")

; Reproduce for 1 generation
; Repeat N times:
; - choose a candidate
; - select the candidate next to him
; - child = cross-over p1 with p2
; - pointMutate child
(defn reproduce [selected popSize crossRate mutationRate]
    (map (fn [x1]
      (let [x2 (nth selected (rand-int popSize))
            child (crossover x1 x2 crossRate)]
          (pointMutate child mutationRate)))
      selected))

; Compare fitness of 2 candidates
(defn cmpFitness [x1 x2]
    (compare (fitness x1) (fitness x2)))

; Main algorithm for genetic search
; - init population
; - sort by fitness, reverse
; - do maxGen times:
;    - binaryTournament
;    - reproduce
;    - record best fitness, break if perfect
(defn evolve []
  ; initialize population
  (def initPop (atom
          (reverse (sort cmpFitness
              (take popSize (repeatedly #(randomGene)))))))

  (doseq [rule @initPop]
    (printRule rule))
  (def best (atom (first @initPop)))

  (genifer6.toClara/prepareClara)

  (loop [i maxGens]
    (println "Gen " i)

    (let [pop1 (reverse (sort cmpFitness
              (take popSize (repeatedly #(binaryTournament @initPop)))))

          pop2 (reverse (sort cmpFitness
              (reproduce pop1 popSize crossRate mutationRate)))]

      (if (>= (fitness (first pop2)) (fitness @best))
        (reset! best (first pop2)))

      (printRule @best)

      (reset! initPop pop2)

      (if (= (fitness @best) 100)
        (println "Success!!!")
        (recur (- i 1))))))

; Uncomment this to run:
; (evolve)
