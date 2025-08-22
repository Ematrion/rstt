from .glicko import Glicko
from ..rating import GlickoRating, Glicko2Rating

import math


class Glicko2(Glicko):
    def __init__(self, mu: float = 1500, tau: float = 0.3, epsilon: float = 0.000000005, *args, **kwargs):
        """Glicko2 Inference

        Implement the `glicko-2 <https://www.glicko.net/glicko/glicko2.pdf>`_ rating system as descried by Prof. Mark E. Glickman.



        Parameters
        ----------
        mu : float, optional
            The default mu of the rating, used to scaled down the GlickoRating, by default 1500.0
        tau: float, optional
            Glicko2 Inference parameter. Tau constrains the change in volatility over time. Reasonable choices are between 0.3 and 1.2, by default 0.3
        epsilon: float, optional
            Glicko2 Inference parameter. Convergence tolerance of the Illinois algorithm used in step 5 of rating update, by default 0.000000005

        .. note::
            Glicko2 is implemented using Glicko Inference with q := 1.0

        """

        super().__init__(q=1, *args, **kwargs)
        # --- system variable --- #
        self.tau = tau  # reasonable choices are between 0.3 and 1.2

        # --- scaling constant --- #
        self.scaling = 173.718
        self.base_mu = mu

        # algorithm constant
        self.epsilon = epsilon
        ''' NOTE on epsilon for _step5
        
        The value does not match
        'The value e = 0.000001 is a sufficiently small choice'
        Does not reproduce the iteration of the calculation example
        e = 0.000000005 does produce very similar numerical values, and number of steps!
        
        Value of A,B fA, fB in step5 iteration
        
        epsilon = 0.00000001 
        -5.626821433520073 -6.126821433520073 -0.0005355033552526004 1.999675064776017
        -5.626821433520073 -5.626955295265377 -0.0002677516776263002 1.5228332788134666e-08
        
        epsilong = 0.000000001
        -5.626821433520073 -6.126821433520073 -0.0005355033552526004 1.999675064776017
        -5.626821433520073 -5.626955295265377 -0.0002677516776263002 1.5228332788134666e-08
        -5.626955295265377 -5.626955287652446 1.5228332788134666e-08 -1.5227465554983055e-08
        -5.626955295265377 -5.626955291458803 7.614166394067333e-09 -0.0005354469812191957
        
        self.epsilon = 0.000000005
        -5.626821433520073 -6.126821433520073 -0.0005355033552526004 1.999675064776017
        -5.626821433520073 -5.626955295265377 -0.0002677516776263002 1.5228332788134666e-08
        -5.626955295265377 -5.626955287652446 1.5228332788134666e-08 -1.5227465554983055e-08
.
        
        '''

        '''
            NOTE:
                - Glicko2 behaves like Glicko with a q parameters set to 1.
                This can be seen when comparing g(phi) of glicko2 with g(RD) in glicko
                This can be seen when comparing v() of glicko2 with d2() of glicko

                - step4, the DELTA function is similar to glicko r' value (Glcko.newRating)
                But I could not figure a clean mathematical relationship.
                Depending on its nature, it could justify a refactoring of Glicko

            FIXME:
                - Glicko2.expectedScore(mu, mu_j, phi_j)  '==' Glicko.expectedScore(r, rj, RDj)
                with base e and  lc constant 1. since the base is not a parameter, we implement an E() method
                This can be improved
        '''

    # --- equations --- #
    # v(): -> glicko.d2 with q = 1
    # g(phi) -> glicko.G with q = 1

    def expectedScore(self, rating1: GlickoRating, rating2: GlickoRating, *args, **kwargs):
        numerator = 1
        denominator = 1 + math.exp(-self.G(rating2.sigma)
                                   * (rating1.mu-rating2.mu)
                                   )
        return numerator / denominator

    def f(self, x: float, phi2: float, delta2: float, v: float, a: float, tau: float):
        numerator = math.exp(x) * (delta2 - phi2 - v - math.exp(x))
        denominator = 2 * (phi2 + v + math.exp(x))**2
        return (numerator / denominator) - ((x - a) / tau**2)

    # --- algorithm --- #
    def _step1(self, tau: float):
        """Ranking Initialisation

        Step 1. description of the algorithm describes operation on the ranking status.
        Not the rating computation process as per RSTT workflow (i.e Inference.rate).
        A system constant is either to be tuned by the ranking.handler, or better, in the ranking.forward

        (a) rating initialisation is not a rstt.inference setting, but a ranking.datamodel one
        (b) most recent rating, i.e ranking.datamodel.get(player), againt not inference related

        Thus _step1 is implemented as a tau set method.

        NOTE:
            - From reading, "system constant"
            I assume tau should be evaluated on the entire rating period, not for each player
            - unclear if it is to be computed every rating period, or tune it once.
        """
        self.tau = tau

    def _step2(self, prior: Glicko2Rating) -> Glicko2Rating:
        return Glicko2Rating(mu=(prior.mu-self.base_mu)/self.scaling,
                             sigma=prior.sigma/self.scaling,
                             volatility=prior.volatility)

    def _step3(self, rating1: GlickoRating, games: list[tuple[GlickoRating, float]]):
        return self.d2(rating1, games)

    def _step4(self, rating1: GlickoRating, games: list[tuple[GlickoRating, float]], v: float) -> float:
        DELTA = sum([self.G(rating2.sigma) * (sj-self.expectedScore(rating1, rating2))
                    for rating2, sj in games])
        return v * DELTA

    def _step5(self, phi2: float, vol2: float, v: float, delta2: float):
        """determine new volatility value, based on Illinois algorithm

            TODO:
                - check procedure's comments
        """

        # 1) set A
        A = math.log(vol2)

        # 2) initial values
        if delta2 > phi2 + v:
            B = math.log(delta2 - phi2 - v)
        else:
            k = 1
            while self.f(A-k*self.tau, phi2, delta2, v, A, self.tau) < 0:
                k = k + 1
                B = A - k*self.tau
                if k == 5:
                    break
            B = A - k*self.tau

        # 3)
        fA = self.f(A, phi2, delta2, v, A, self.tau)
        fB = self.f(B, phi2, delta2, v, A, self.tau)
        # 4)
        while abs(B-A) > self.epsilon:
            # (a)
            C = A+(A-B)*fA/(fB-fA)
            fC = self.f(C, phi2, delta2, v, A, self.tau)

            # (b)
            if fC*fB <= 0:
                A = B
                fA = fB
            else:
                fA = fA/2

            # (c)
            B = C
            fB = fC

            # (d) is the while condition

        # 5) post volatility
        return math.exp(A/2)

    def _step6(self, phi: float, volatility: float):
        return math.sqrt(phi**2 + volatility**2)

    def _step7(self, rating: GlickoRating, phi_star: float, v: float, games: list[tuple[GlickoRating, float]]):
        phi_prime = 1 / math.sqrt(1/phi_star**2 + 1/v)
        mu_prime = rating.mu + phi_prime**2 * sum([self.G(rj.sigma)*(sj - self.expectedScore(rating, rj))
                                                   for rj, sj in games])
        return mu_prime, phi_prime

    def _step8(self, mu_prime: float, phi_prime: float):
        mu = self.scaling * mu_prime + self.base_mu
        sigma = self.scaling * phi_prime
        return mu, sigma

    # --- Inference --- #
    def rate(self, rating: Glicko2Rating, ratings_opponents: list[Glicko2Rating], scores: list[float]):
        # !!! self._step1(...) needs to be performed in the forward method
        '''
        NOTE: scaling up and down rating
            - within the rate method increase number of operation.
            - within the forward method makes it harder to read and maintain.
        '''

        # step2 - scaling down
        r = self._step2(rating)
        rs = [self._step2(opp) for opp in ratings_opponents]

        # NOTE: unecessary formating -> change method signature
        games = [(rating, score)
                 for rating, score in zip(rs, scores)]

        # perform steps
        v = self._step3(r, games)
        delta = self._step4(r, games, v)
        post_volatility = self._step5(r.sigma**2,
                                      r.volatility**2,
                                      v, delta**2)
        phi_star = self._step6(phi=r.sigma,
                               volatility=post_volatility)
        mu_prime, phi_prime = self._step7(r, phi_star, v, games)
        post_mu, post_rd = self._step8(mu_prime, phi_prime)

        return Glicko2Rating(post_mu, post_rd, post_volatility)


'''
TODO:
    - User & Dev DocString
    - Add author comments and Note
    - Check default values
    - What about predictions ?
    - Edit docs/*.rst files to include new features
    - add Glicko2 Ranking
    - CleanUp Code
    - CleanUp Test
    - merge glikco 1&2 test variables ?
'''
