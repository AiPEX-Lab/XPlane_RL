from gym.envs.registration import register

register(
    id='gymXplane-v2',
    entry_point='gym_xplane.envs:XplaneEnv',
    kwargs={'xpHost':'127.0.0.1', 'xpPort':49009,'timeout':3000}
)
