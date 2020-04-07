# Kanban

## Ready For Dev

* Support Leader Capture mechanic
* Support Kwizatz Haderach
* Support Special Treachery Cards
* Support ANY TIME Karama powers
* Show battle round state
  * What leaders have been used
  * What battle powers have been "karamed"
  * What has been voiced
  * What has been prescienced
* Improve widgets for battle round
  * Battle Plan Selection
  * Voice Selection
  * Prescience Selection

## In Progress


## Done
* Show the discard piles on the board
* Switch to using websockets instead of polling
* Re-do BG coexist in a reasonable way
  * There shouldn't be any union arg specs with "coexist" constants, rather a ¿coexist? check command should happen before the movement resolves
    * This check happens when you move from a coexist into an occupied territory where you do not already have fighthers
    * This check happens when someone else moves into a territory you were the sole occupier of
  * There shouldn't be a coexist persist option but rather the option to flip at any time before shipments occur
* Break up the Unions

# Notes

## Karama Powers ##

  * ANY TIME:
    * H KARAMA take treachery cards
    * E KARAMA revive 3 or leaders
    * block B worthless Karama
    * F KARAMA make worm show up (Restricted to SPICE and MOVEMENT)

  * STORM

  * SPICE

  * NEXUS
    * block F worm ride

  * BIDDING
    * block extra H card
    * Block A looking at hidden card
    * free treachery

  * REVIVAL

  * MOVEMENT
    * Make Guild go in turn order
    * Cheap shipment
    * Block B spiritual guide
    * G KARAMA prevent shipment

  * BATTLE
    * block A prescience
    * block B voice
    * Block H leader capture
    * Block A kwizatz haderach
    * Weaken F 2's
    * Weak E 2's
    * A KARAMA look at b entire plan

  * COLLECTION


## Special Treachery ##

    * ANY TIME:
      * Tleilaxu Ghola
      * Truthtrance

    * STORM
      * Weather Control
      * Family Atomics

    * SPICE
      * Harvester
      * Thumper

    * NEXUS

    * BIDDING

    * REVIVAL

    * MOVEMENT
      * Harj

    * BATTLE

    * COLLECTION
