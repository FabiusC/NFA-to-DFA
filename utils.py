class LambdaManager:
    LAMBDA_SYMBOL = "ʎ"  # Símbolo lambda utilizado en transiciones
    SAFE_REPRESENTATION = "<lambda>"  # Representación alternativa para impresión segura

    @staticmethod
    def replace_lambda_for_print(text):
        """
        Reemplaza el símbolo `ʎ` con una representación segura para impresión o depuración.
        :param text: Cadena de texto que puede contener `ʎ`.
        :return: Cadena con `ʎ` reemplazado por `<lambda>`.
        """
        return text.replace(LambdaManager.LAMBDA_SYMBOL, LambdaManager.SAFE_REPRESENTATION)

    @staticmethod
    def insert_lambda(entry_widget):
        """
        Inserta el símbolo `ʎ` en un widget de entrada (como un Entry de Tkinter).
        :param entry_widget: Widget donde se insertará el símbolo.
        """
        entry_widget.insert('end', LambdaManager.LAMBDA_SYMBOL)

    @staticmethod
    def is_lambda_symbol(text):
        """
        Verifica si un texto es exactamente el símbolo lambda.
        :param text: Texto a verificar.
        :return: True si el texto es `ʎ`, de lo contrario False.
        """
        return text == LambdaManager.LAMBDA_SYMBOL
