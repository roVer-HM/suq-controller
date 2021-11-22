from suqc.utils.SeedManager import SeedManager

if __name__ == "__main__":
    simple_dict = [{"a": "a"}, {"b": "b"}]
    s = SeedManager(simple_dict, 2)
    repeated_dicts = s._create_repeated_seed_variations(variations=simple_dict, repetitions=3)
    # no_seed = s.add_vadere_seed(par_variation, fixed_seed=True)
    # fixed_seed = s.add_vadere_seed(par_variation, fixed_seed=True)
    # random_seed = s.add_vadere_seed(par_variation, fixed_seed=False)
    print("breakpoint")
