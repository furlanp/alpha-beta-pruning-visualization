# Alpha-Beta Visualizer

This is an Alpha-Beta algorithm visualizer tool built using Python and Tkinter. 

## What is Alpha-Beta algorithm?

[Alpha-Beta](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning) is a search algorithm commonly used in two-player games to determine the right move.
It is similar to [Minimax](https://en.wikipedia.org/wiki/Minimax) algorithm but has additional parameters, _alpha_ and _beta_, enabling the pruning of the search tree.

## Installation
 
### Clone repository
~~~ 
git clone https://github.com/furlanp/alpha-beta-pruning-visualization.git
cd alpha-beta-pruning-visualization
~~~

### Install tkinter
~~~
pip install tkinter
~~~

### Run the app
~~~
python alpha-beta.py
~~~ 

## Usage

### Generate tree
To generate tree, you have to provide tree structure and leaf values. Tree structure is a string that defines number of children for nodes in each layer. 
Leaf values is a string that defines values for nodes on the last layer.

Tree structure uses the following format: `n|m1,m2,m3|...`, where `n` denotes number of children for root, `m1,m2,m3` denotes number of children for nodes on second layer and so on.

Leaf values uses the following format: `v1,v2,v3...` .

### Controls
Once the tree is generated, use controls to simulate Alpha-Beta algorithm. 
There are four type of controls available:
* one step forward (>>)
* one step backward (<<)
* all steps forward (>>>)
* all steps backward (<<<)

### Handling large trees
It can happen that the input generates a tree that is too large to fit the canvas. In that case, drag the tree around with your mouse to view different parts of tree. You can also use mouse-wheel for zooming in and out.

## Demo

https://github.com/furlanp/alpha-beta-pruning-visualization/assets/73120926/5f9b29e2-eadf-4cbb-b09a-ce58765cf890


