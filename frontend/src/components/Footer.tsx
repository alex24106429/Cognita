import React, { useEffect, useState } from 'react';
import { Anchor, Badge, Box, Divider, Group, Text } from '@mantine/core';
import { IconHeartHandshake } from '@tabler/icons-react';

import { checkHealth, API_BASE_URL } from '../utils/api';
import type { ThemePalette } from '../types';

interface Props {
  palette: ThemePalette;
}

interface ModelMetadata {
  model: string;
  baseUrl: string;
  keyConfigured: boolean;
}

export const Footer: React.FC<Props> = ({ palette }) => {
  const [metadata, setMetadata] = useState<ModelMetadata | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    checkHealth(controller.signal)
      .then((health) =>
        setMetadata({
          model: health.model,
          baseUrl: health.base_url,
          keyConfigured: health.api_key_configured,
        })
      )
      .catch(() => setMetadata(null));
    return () => controller.abort();
  }, []);

  return (
    <Box
      component="footer"
      mt="xl"
      pt="lg"
      style={{ borderTop: `1px solid ${palette.border}`, color: palette.mutedText }}
    >
      <Group gap="xs" mb="xs" wrap="wrap">
        <IconHeartHandshake size={16} color={palette.accent} aria-hidden />
        <Text size="xs" fw={600}>
          SDG 10: Reduced Inequalities — Targets 10.2 & 10.3
        </Text>
        <Badge size="xs" variant="light" color="indigo">
          Hackathon 3 submission
        </Badge>
      </Group>

      <Text size="xs" mb={6} maw={760}>
        <strong>Ethical notice.</strong> Cognita is a cognitive accessibility scaffold, not an
        exam substitute. Summarisation can flatten methodological qualifiers, so always verify
        exam-critical claims against the highlighted passage in your original source document.
        Advanced terminology is intentionally preserved rather than simplified.
      </Text>

      <Divider my="xs" />

      <Group justify="space-between" wrap="wrap" gap="xs">
        <Text size="xs">
          {metadata
            ? `Model: ${metadata.model} · Endpoint: ${metadata.baseUrl}${
                metadata.keyConfigured ? '' : ' · API key not configured'
              }`
            : `Backend: ${API_BASE_URL} (unreachable)`}
        </Text>
        <Anchor
          size="xs"
          href="https://sdgs.un.org/goals/goal10"
          target="_blank"
          rel="noopener noreferrer"
        >
          UN SDG 10 documentation
        </Anchor>
      </Group>
    </Box>
  );
};
