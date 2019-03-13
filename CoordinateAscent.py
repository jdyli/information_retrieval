from random import shuffle

"""
This file is based on https://github.com/tmanabe/coordinate-ascent. The original code was modified to use different
parameters, normalize the parameters to a length of 1, and enforcing all parameters to be positive.
"""


class CoordinateAscent(object):
    def __init__(self, evaluate, n_restart=1, n_max_iteration=1, step_base=0.05, step_scale=2.0, tolerance=0.001):
        self.evaluate = evaluate
        self.n_restart = n_restart
        self.n_max_iteration = n_max_iteration
        self.step_base = step_base
        self.step_scale = step_scale
        self.tolerance = tolerance

    @staticmethod
    def normalize(params):
        length = params["page_title"] + params["col_title"] + params["body"] + params["sec_title"] + \
                 params["caption"]
        params["page_title"] /= length
        params["col_title"] /= length
        params["body"] /= length
        params["sec_title"] /= length
        params["caption"] /= length

    def learn(self, params):
        keys = list(params.keys())
        regular_params, global_start_score = params.copy(), self.evaluate(params)
        global_best_params, global_best_score = regular_params.copy(), global_start_score

        for _ in range(self.n_restart):
            consecutive_fails = 0
            params = regular_params.copy()
            best_params, best_score = regular_params.copy(), global_start_score

            while consecutive_fails < len(keys):
                start_score = best_score
                shuffle(keys)

                for currentKey in keys:
                    original_value, best_total_step, succeeds = params.copy(), 0.0, False

                    for direction in [1, -1, 0]:
                        step = 0.01 * direction
                        if 0.0 != original_value[currentKey] and abs(original_value[currentKey]) < 2 * abs(step):
                            step = self.step_base * abs(original_value[currentKey])
                        total_step, n_iteration = step, self.n_max_iteration
                        if 0 == direction:
                            total_step, n_iteration = -original_value[currentKey], 1

                        for _ in range(n_iteration):
                            params[currentKey] = original_value[currentKey] + total_step
                            if params[currentKey] < 0:
                                params[currentKey] = 0
                            self.normalize(params)
                            score = self.evaluate(params)
                            if score is not None and best_score < score:
                                best_score, best_total_step, succeeds = score, total_step, True
                            step *= self.step_scale
                            total_step += step

                        if succeeds:
                            break

                    if succeeds:
                        consecutive_fails = 0
                        params = original_value
                        params[currentKey] = original_value[currentKey] + best_total_step
                        self.normalize(params)
                        best_params = params.copy()
                    else:
                        consecutive_fails += 1
                        params = original_value

                if best_score - start_score < self.tolerance:
                    break

            if global_best_score < best_score:
                global_best_score, global_best_params = best_score, best_params.copy()

        return global_best_params
