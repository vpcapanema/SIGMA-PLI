-- Migration 011: Criar função e trigger para sincronizar usuarios.usuario -> cadastro.pessoa
-- Esta migração cria a função que garante a criação/atualização de um registro em cadastro.pessoa
-- sempre que um usuário for inserido/atualizado na tabela usuarios.usuario.
-- Observação: a função usa gen_random_uuid() para gerar ids quando necessário (pgcrypto).

BEGIN;

    -- criar função de sincronização
    CREATE OR REPLACE FUNCTION usuarios.sync_usuario_to_cadastro_pessoa
    ()
RETURNS trigger
LANGUAGE plpgsql
AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
        -- Se usuario não tem pessoa_id, crie uma pessoa em cadastro.pessoa e vincule
        IF NEW.pessoa_id IS NULL THEN
            NEW.pessoa_id := gen_random_uuid
        ();
    INSERT INTO cadastro.pessoa
        (
        id, nome_completo, cpf, email, telefone, ativa, created_at
        )
    VALUES
        (
            NEW.pessoa_id,
            COALESCE(NEW.username, NEW.email_institucional, ''),
            NULL,
            NEW.email_institucional,
            NEW.telefone_institucional,
            TRUE,
            NOW()
            );
    ELSE
    -- Se já existe pessoa referenciada, atualizar/inserir
    IF EXISTS(SELECT 1
    FROM cadastro.pessoa
    WHERE id = NEW.pessoa_id) THEN
    UPDATE cadastro.pessoa
                SET email = COALESCE(NEW.email_institucional, email),
                    telefone = COALESCE(NEW.telefone_institucional, telefone)
                WHERE id = NEW.pessoa_id;
    ELSE
    INSERT INTO cadastro.pessoa
        (
        id, nome_completo, cpf, email, telefone, ativa, created_at
        )
    VALUES
        (
            NEW.pessoa_id,
            COALESCE(NEW.username, NEW.email_institucional, ''),
            NULL,
            NEW.email_institucional,
            NEW.telefone_institucional,
            TRUE,
            NOW()
                );
END
IF;
        END
IF;

    ELSIF
(TG_OP = 'UPDATE') THEN
-- On update, propagate email/phone changes to cadastro.pessoa if linked
IF NEW.pessoa_id IS NOT NULL THEN
IF EXISTS(SELECT 1
FROM cadastro.pessoa
WHERE id = NEW.pessoa_id) THEN
UPDATE cadastro.pessoa
                SET email = COALESCE(NEW.email_institucional, email),
                    telefone = COALESCE(NEW.telefone_institucional, telefone)
                WHERE id = NEW.pessoa_id;
ELSE
-- If the person does not exist, create it
INSERT INTO cadastro.pessoa
    (
    id, nome_completo, cpf, email, telefone, ativa, created_at
    )
VALUES
    (
        NEW.pessoa_id,
        COALESCE(NEW.username, NEW.email_institucional, ''),
        NULL,
        NEW.email_institucional,
        NEW.telefone_institucional,
        TRUE,
        NOW()
                );
END
IF;
        ELSE
            -- If pessoa_id was removed/cleared, create a new cadastro.pessoa and link it
            NEW.pessoa_id := gen_random_uuid
();
INSERT INTO cadastro.pessoa
    (
    id, nome_completo, cpf, email, telefone, ativa, created_at
    )
VALUES
    (
        NEW.pessoa_id,
        COALESCE(NEW.username, NEW.email_institucional, ''),
        NULL,
        NEW.email_institucional,
        NEW.telefone_institucional,
        TRUE,
        NOW()
            );
END
IF;
    END
IF;

    RETURN NEW;
END;
$$;

-- Cria trigger na tabela usuarios.usuario que chama a função antes de INSERT ou UPDATE
DROP TRIGGER IF EXISTS trigger_sync_usuario_to_cadastro_pessoa
ON usuarios.usuario;
CREATE TRIGGER trigger_sync_usuario_to_cadastro_pessoa
BEFORE
INSERT OR
UPDATE ON usuarios.usuario
FOR EACH ROW
EXECUTE FUNCTION usuarios
.sync_usuario_to_cadastro_pessoa
();

COMMIT;
