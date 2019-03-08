from random import shuffle


class CoorAscent(object):
    def __init__(self,
                 evaluate,
                 validate=None,
                 nRestart=1,
                 nMaxIteration=1,
                 stepBase=0.05,
                 stepScale=2.0,
                 tolerance=0.001):
        assert 'function' == evaluate.__class__.__name__
        self.evaluate = evaluate
        if validate is not None:
            assert 'function' == validate.__class__.__name__
        self.validate = validate

        self.nRestart = nRestart
        self.nMaxIteration = nMaxIteration
        self.stepBase = stepBase
        self.stepScale = stepScale
        self.tolerance = tolerance

    def learn(self, params):
        keys = list(params.keys())
        regularParams, globalStartScore = params.copy(), self.evaluate(params)
        assert globalStartScore is not None
        globalBestParams, globalBestScore = regularParams.copy(), globalStartScore

        for _ in range(self.nRestart):
            consecutiveFails = 0
            params = regularParams.copy()
            bestParams, bestScore = regularParams.copy(), globalStartScore

            while consecutiveFails < len(keys):
                startScore = bestScore
                shuffle(keys)

                for currentKey in keys:
                    originalValue, bestTotalStep, succeeds = params.copy(), 0.0, False

                    for direction in [1, -1, 0]:
                        step = 0.01 * direction
                        if 0.0 != originalValue[currentKey] and abs(originalValue[currentKey]) < 2 * abs(step):
                            step = self.stepBase * abs(originalValue[currentKey])
                        totalStep, nIteration = step, self.nMaxIteration
                        if 0 == direction:
                            totalStep, nIteration = -originalValue[currentKey], 1

                        for _ in range(nIteration):
                            params[currentKey] = originalValue[currentKey] + totalStep
                            if params[currentKey] < 0:
                                params[currentKey] = 0
                            length = params["page_title"] + params["col_title"] + params["body"] + params["sec_title"] + params["caption"]
                            params["page_title"] /= length
                            params["col_title"] /= length
                            params["body"] /= length
                            params["sec_title"] /= length
                            params["caption"] /= length
                            score = self.evaluate(params)
                            if score is not None and bestScore < score:
                                bestScore, bestTotalStep, succeeds = score, totalStep, True
                            step *= self.stepScale
                            totalStep += step

                        if succeeds:
                            break

                    if succeeds:
                        consecutiveFails = 0
                        params = originalValue
                        params[currentKey] = originalValue[currentKey] + bestTotalStep
                        length = params["page_title"] + params["col_title"] + params["body"] + params["sec_title"] + params["caption"]
                        params["page_title"] /= length
                        params["col_title"] /= length
                        params["body"] /= length
                        params["sec_title"] /= length
                        params["caption"] /= length
                        bestParams = params.copy()
                    else:
                        consecutiveFails += 1
                        params = originalValue
                    print("params: " + str(params))

                if (bestScore - startScore < self.tolerance):
                    break

            if self.validate is not None:
                bestScore = self.validate(bestParams)
            if globalBestScore < bestScore:
                globalBestScore, globalBestParams = bestScore, bestParams.copy()

        return globalBestParams
