Require Import Coq.NArith.NArith.
Require Import Coq.Lists.List.
Import ListNotations.
Open Scope N_scope.

Definition mask (n x : N) : N := N.land x (N.pred (N.pow 2 n)).

Definition rotl (n x k : N) : N :=
  mask n (N.lor (N.shiftl x k) (N.shiftr x (n - k))).

Definition rotr (n x k : N) : N :=
  mask n (N.lor (N.shiftr x k) (N.shiftl x (n - k))).

Fixpoint repeat_1D_nat (m : nat) : N :=
  match m with
  | O => 0
  | S m' => N.lor (N.shiftl (repeat_1D_nat m') 8) 29
  end.

Definition constant_of_width (n : N) : N := repeat_1D_nat (N.to_nat (N.div n 8)).

Definition delta (n x : N) : N :=
  mask n
    (N.lxor
      (N.lxor
        (N.lxor (rotl n x 1) (rotl n x 3))
        (rotr n x 2))
      (constant_of_width n)).

Fixpoint sequence (steps : nat) (n seed : N) : list N :=
  match steps with
  | O => []
  | S k => seed :: sequence k n (delta n seed)
  end.

Theorem delta_deterministic :
  forall n x y, x = y -> delta n x = delta n y.
Proof.
  intros n x y H; now rewrite H.
Qed.

Theorem sequence_deterministic :
  forall steps n x y, x = y -> sequence steps n x = sequence steps n y.
Proof.
  intros steps n x y H; now rewrite H.
Qed.

Theorem mask_idempotent :
  forall n x, mask n (mask n x) = mask n x.
Proof.
  intros n x.
  unfold mask.
  rewrite N.land_assoc.
  rewrite N.land_diag.
  reflexivity.
Qed.
