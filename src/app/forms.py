from wtforms_alchemy import ModelForm as BaseModelForm


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        from starlette_core.database import Session

        return Session()
