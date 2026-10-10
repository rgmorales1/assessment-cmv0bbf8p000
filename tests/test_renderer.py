from app.services.renderer import render_notarial_deed


def test_render_notarial_deed_interpolation():
    client_dict = {
        "rut": "15.342.198-4",
        "full_name": "Juan Pablo Morales Sepulveda",
        "email": "j.morales@example.cl",
        "address": "Av. Providencia 1240",
        "commune": "Providencia",
    }
    metadata = {
        "document_code": "DOC-2024-8841",
        "deed_type": "PODER_ESPECIAL",
        "created_at": "14 de octubre de 2024",
    }
    result = render_notarial_deed("PODER_ESPECIAL", client_dict, metadata)
    assert "Juan Pablo Morales Sepulveda" in result
    assert "estado civil no informado" in result
    assert "profesion u oficio no informado" in result


def test_render_notarial_deed_blank_civil_status_and_profession():
    client_dict = {
        "rut": "15.342.198-4",
        "full_name": "Juan Pablo Morales Sepulveda",
        "estado_civil": "",
        "profesion_oficio": "   ",
    }
    metadata = {"document_code": "DOC-2024-8841", "deed_type": "PODER_ESPECIAL"}
    result = render_notarial_deed("PODER_ESPECIAL", client_dict, metadata)
    assert "estado civil no informado" in result
    assert "profesion u oficio no informado" in result


def test_render_notarial_deed_with_civil_status_and_profession():
    client_dict = {
        "rut": "18.234.567-8",
        "full_name": "Francisca Andrea Silva Castro",
        "estado_civil": "Soltera",
        "profesion_oficio": "Ingeniera Comercial",
    }
    metadata = {"document_code": "DOC-2024-8845", "deed_type": "PODER_ESPECIAL"}
    result = render_notarial_deed("PODER_ESPECIAL", client_dict, metadata)
    assert "estado civil Soltera" in result
    assert "profesion u oficio Ingeniera Comercial" in result
    assert "no informado" not in result


def test_render_general_power_without_civil_status_and_profession():
    client_dict = {
        "rut": "15.342.198-4",
        "full_name": "Juan Pablo Morales Sepulveda",
    }
    metadata = {"document_code": "DOC-2024-8841", "deed_type": "PODER_GENERAL"}
    result = render_notarial_deed("PODER_GENERAL", client_dict, metadata)
    assert "estado civil no informado" in result
    assert "de profesion u oficio no informado" in result
