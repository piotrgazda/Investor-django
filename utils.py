

from django.template.loader import render_to_string


def fading_sections(sections, names):
    if len(sections) != len(names):
        raise ValueError(
            "Sections length doesn't match length of names in navigation. ")
    return render_to_string(template_name='fading-sections.html', context={'names_sections': list(zip(names, sections))})

