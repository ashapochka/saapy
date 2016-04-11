from saapy.dsl import model


def test_basic_model():
    m = model()
    cms_platform = m.decisions("Select CMS Platform")
    dev_costs, support_costs, fun_suitability, prod_quality = m.uncertainties(
        "Development Costs", "Support Costs",
        "Functional Suitability", "Product Quality")
    cms_platform.relates_to(dev_costs, support_costs,
                            fun_suitability, prod_quality)
    total_value = m.uncertainties("Total Value")
    total_value.depends_on(dev_costs, support_costs,
                           fun_suitability, prod_quality)
    assert 6 == len(m.graph)
    assert 8 == m.graph.size()
