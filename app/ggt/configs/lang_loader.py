import yaml

language_file = './lang.yml'


# This function loads the language file and convert the yaml into a dictionary
def __load_lang_configs(lang_file):
    with open(lang_file) as file:
        lang_configs = yaml.safe_load(file)
        return lang_configs


def load_languages(lang_file: str = language_file):
    return __load_lang_configs(lang_file)
