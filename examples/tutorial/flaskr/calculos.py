#Descrição: Refatoração da aplicação Flaskr para arquitetura MVC utilizando Flask-SQLAlchemy, Bootstrap 5, upload de arquivos e cálculos financeiros em memória
#Nome_arquivo: calculos.py
#Nome_exercicio: Prova Desenvolvimento Web 2 - 24/11/2026
#Nome: Eduardo Rodrigues de Novaes
#email: eduardo.novaes@aluno.cps.sp.gov.br
#Turma: 2º turma DSM Fatec Olimpia

from flask import Blueprint, flash, render_template, request

bp = Blueprint("calculos", __name__, url_prefix="/calculos")


def calcular_irpf(salario_bruto: float) -> dict:
    """
    Calcula a alíquota e o desconto estimado de IRPF em memória
    com base na tabela progressiva mensal.
    """
    if salario_bruto <= 2259.20:
        aliquota = 0.0
        deducao = 0.0
        faixa = "Isento (0%)"
    elif salario_bruto <= 2826.65:
        aliquota = 0.075
        deducao = 169.44
        faixa = "7,5%"
    elif salario_bruto <= 3751.05:
        aliquota = 0.15
        deducao = 381.44
        faixa = "15%"
    elif salario_bruto <= 4664.68:
        aliquota = 0.225
        deducao = 662.77
        faixa = "22,5%"
    else:
        aliquota = 0.275
        deducao = 896.00
        faixa = "27,5%"

    desconto = max(0.0, (salario_bruto * aliquota) - deducao)
    salario_liquido = salario_bruto - desconto

    return {
        "salario_bruto": salario_bruto,
        "faixa": faixa,
        "desconto": desconto,
        "salario_liquido": salario_liquido,
    }


def calcular_decimo_terceiro(salario_base: float, meses_trabalhados: int) -> dict:
    """
    Calcula o valor proporcional aproximado do 13º salário na rescisão.
    """
    valor_proporcional = (salario_base / 12.0) * meses_trabalhados
    return {
        "salario_base": salario_base,
        "meses_trabalhados": meses_trabalhados,
        "valor_proporcional": valor_proporcional,
    }


@bp.route("/painel", methods=("GET", "POST"))
def painel():
    resultado_irpf = None
    resultado_rescisao = None

    if request.method == "POST":
        tipo_calculo = request.form.get("tipo_calculo")

        if tipo_calculo == "irpf":
            try:
                salario_bruto = float(request.form.get("salario_bruto", 0))
                if salario_bruto <= 0:
                    flash("Informe um salário bruto maior que zero.", "danger")
                else:
                    resultado_irpf = calcular_irpf(salario_bruto)
            except ValueError:
                flash("Valor inválido para o salário bruto.", "danger")

        elif tipo_calculo == "rescisao":
            try:
                salario_base = float(request.form.get("salario_base", 0))
                meses_trabalhados = int(request.form.get("meses_trabalhados", 0))
                if salario_base <= 0 or not (1 <= meses_trabalhados <= 12):
                    flash(
                        "Informe um salário base válido e meses entre 1 e 12.",
                        "danger",
                    )
                else:
                    resultado_rescisao = calcular_decimo_terceiro(
                        salario_base, meses_trabalhados
                    )
            except ValueError:
                flash("Valores inválidos para o cálculo de rescisão.", "danger")

    return render_template(
        "calculos/index.html",
        resultado_irpf=resultado_irpf,
        resultado_rescisao=resultado_rescisao,
    )