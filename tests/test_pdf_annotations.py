import inspect
from Applications import franny


def test_injection_contains_bridge_functions():
    source = inspect.getsource(franny.PDFViewerTab.inject_annotation_js)
    assert 'frannyGetAnnotations' in source
    assert 'frannyExportCanvas' in source
    assert 'frannyLoadAnnotations' in source
