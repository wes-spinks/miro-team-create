#! /bin/sh
var_list="MIRO_TOKEN"

export_vars() {
    secret_missing="false"
    if [ -z "$SECRETS_DIR" ]; then
        export SECRETS_DIR="/secrets"
    fi
    for f in "${@}"; do
        echo "$f"
        fname="${SECRETS_DIR}/${f}"
        if [ -f "${fname}" ]; then
            if [ -s "${fname}" ]; then
                if grep "<No Value>" ${fname};then
                    echo "No Value for secret $f; Please check Vault for entry"
                    secret_missing="true"
                fi
                export "$f"="$(< ${fname})"
            else
                echo "empty file $f."
                secret_missing="true"
            fi
        else
            echo "$f not present."
            secret_missing="true"
        fi
    done
    [[ "$secret_missing" == "false" ]] && return 0 || return 2;
}

sleep 5 && export_vars ${var_list} || return 1

