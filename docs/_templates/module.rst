{{ objname | escape | underline}}

.. automodule:: {{ fullname }}

    {% block functions %}
    {% if functions %}
    .. rubric:: Functions
	
    .. autosummary::
        :template: base.rst
        :toctree:
        :nosignatures:
        {% for item in functions %}
        {{ item }}
        {%- endfor %}
        {% endif %}
        {% endblock %}

    {% block classes %}
    {% if classes %}
    .. rubric:: Classes

    .. autosummary::
        :template: class.rst
        :toctree:
        {% for item in classes %}
        {{ item }}
        {%- endfor %}
        {% endif %}
        {% endblock %}
	
    {% block exceptions %}
    {% if exceptions %}
    .. rubric:: Exceptions
	
    .. autosummary::
        :toctree:
        {% for item in exceptions %}
        {{ item }}
        {%- endfor %}
        {% endif %}
        {% endblock %}
