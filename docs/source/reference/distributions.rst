Probability Distributions
=========================

.. module:: chainer.distributions

Chainer provides many :class:`~chainer.Distribution` implementations in the
:mod:`chainer.distributions` package.


Distributions
-------------

.. autosummary::
   :toctree: generated/
   :nosignatures:
   
   chainer.distributions.Bernoulli
   chainer.distributions.Laplace
   chainer.distributions.MultivariateNormal
   chainer.distributions.Normal


Functionals of distribution
---------------------------

.. currentmodule:: chainer

.. autosummary::
  :toctree: generated/
  :nosignatures:
  
  chainer.cross_entropy
  chainer.kl_divergence
  chainer.register_kl


Base classes
------------

.. autosummary::
  :toctree: generated/
  :nosignatures:

  chainer.Distribution
